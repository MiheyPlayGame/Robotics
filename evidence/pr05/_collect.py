"""Collect PR05 QoS evidence against an already-running turtlesim.

Expects ROS env sourced, ROS_DOMAIN_ID set, turtlesim publishing /turtle1/pose.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
DOMAIN = os.environ.get('ROS_DOMAIN_ID', '16')
BAG_DIR = EVIDENCE / 'bag'
POSE_TYPE = 'turtlesim_msgs/msg/Pose'
CHILDREN: list[subprocess.Popen[bytes]] = []


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env['ROS_DOMAIN_ID'] = DOMAIN
    return env


def run(
    args: list[str],
    *,
    timeout: float | None = 30,
) -> subprocess.CompletedProcess[str]:
    print('+', ' '.join(args), flush=True)
    return subprocess.run(
        args,
        cwd=str(ROOT),
        env=_env(),
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def write(name: str, text: str) -> None:
    path = EVIDENCE / name
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'wrote {path} ({len(text)} bytes)', flush=True)


def start_bg(
    args: list[str],
    log_name: str,
    *,
    new_group: bool = False,
) -> subprocess.Popen[bytes]:
    log_path = EVIDENCE / log_name
    log_file = open(log_path, 'w', encoding='utf-8', errors='replace')
    print('+', ' '.join(args), '>', log_path.name, flush=True)
    kwargs: dict = {
        'cwd': str(ROOT),
        'env': _env(),
        'stdout': log_file,
        'stderr': subprocess.STDOUT,
    }
    if new_group and os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(args, **kwargs)
    proc._log_file = log_file  # type: ignore[attr-defined]
    CHILDREN.append(proc)
    return proc


def stop_children() -> None:
    for proc in list(CHILDREN):
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        log_file = getattr(proc, '_log_file', None)
        if log_file is not None:
            try:
                log_file.close()
            except Exception:
                pass
    CHILDREN.clear()
    # Kill leftover namespaced nodes from prior runs; keep turtlesim.
    subprocess.run(
        [
            'powershell', '-NoProfile', '-Command',
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -match "
            "'patrol.launch|pose_relay|qos_probe|/robot_a|bag record|bag play|"
            "lib\\\\patrol\\\\patrol|patrol.exe' "
            "-and $_.CommandLine -notmatch 'turtlesim_node' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force "
            "-ErrorAction SilentlyContinue }",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    time.sleep(2)


def diagnose() -> str:
    parts: list[str] = []
    for args in (
        ['ros2', 'node', 'list'],
        ['ros2', 'topic', 'list'],
        ['ros2', 'topic', 'info', '/turtle1/pose', '-v'],
        ['ros2', 'topic', 'info', '/robot_a/sensor_pose', '-v'],
    ):
        try:
            result = run(args, timeout=15)
            parts.append(
                f"$ {' '.join(args)}\n"
                f"{result.stdout or ''}{result.stderr or ''}"
            )
        except subprocess.TimeoutExpired:
            parts.append(f"$ {' '.join(args)}\n[timeout]\n")
    return '\n'.join(parts)


def wait_topic(name: str, seconds: float = 30.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            result = run(['ros2', 'topic', 'list'], timeout=10)
        except subprocess.TimeoutExpired:
            time.sleep(1)
            continue
        if name in (result.stdout or '').splitlines():
            return True
        time.sleep(1)
    return False


def topic_has_publisher(name: str) -> bool:
    try:
        result = run(['ros2', 'topic', 'info', name], timeout=10)
    except subprocess.TimeoutExpired:
        return False
    text = (result.stdout or '') + (result.stderr or '')
    for line in text.splitlines():
        if 'Publisher count' in line:
            digits = ''.join(ch for ch in line if ch.isdigit())
            return bool(digits) and int(digits) > 0
    return False


def wait_subscription(topic: str, seconds: float = 20.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            result = run(['ros2', 'topic', 'info', topic], timeout=10)
        except subprocess.TimeoutExpired:
            time.sleep(1)
            continue
        text = result.stdout or ''
        for line in text.splitlines():
            if 'Subscription count' in line:
                digits = ''.join(ch for ch in line if ch.isdigit())
                if digits and int(digits) > 0:
                    return True
        time.sleep(1)
    return False


def echo_once(reliability: str, timeout_s: float = 5.0) -> tuple[str, bool]:
    """Use in-process rclpy receiver — CLI echo often loses the DDS race on Windows."""
    args = [
        'python', str(EVIDENCE / '_recv_once.py'),
        '--reliability', reliability,
        '--timeout', str(timeout_s),
    ]
    print('+', ' '.join(args), flush=True)
    try:
        result = subprocess.run(
            args,
            cwd=str(ROOT),
            env=_env(),
            text=True,
            capture_output=True,
            timeout=timeout_s + 5,
        )
    except subprocess.TimeoutExpired as error:
        text = (error.stdout or '') + (error.stderr or '')
        text += f'\n[timeout/no message] reliability={reliability}\n'
        return text, False
    text = (result.stdout or '') + (result.stderr or '')
    got = result.returncode == 0 and (
        ('x:' in text.lower()) or ('theta:' in text.lower())
    )
    return text, got


def start_nodes(reliability: str, log_prefix: str) -> None:
    """Start pose_relay + qos_probe + patrol via ros2 run (same graph as launch)."""
    start_bg(
        [
            'ros2', 'run', 'course_bringup', 'pose_relay',
            '--ros-args', '-r', '__ns:=/robot_a',
        ],
        f'{log_prefix}-pose_relay.log',
    )
    start_bg(
        [
            'ros2', 'run', 'course_bringup', 'qos_probe',
            '--ros-args',
            '-r', '__ns:=/robot_a',
            '-p', f'reliability:={reliability}',
        ],
        f'{log_prefix}-qos_probe.log',
    )
    start_bg(
        [
            'ros2', 'run', 'patrol', 'patrol',
            '--ros-args',
            '-r', '__ns:=/robot_a',
            '-r', 'cmd_vel:=/turtle1/cmd_vel',
        ],
        f'{log_prefix}-patrol.log',
    )


def wait_sensor_flow(seconds: float = 25.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        _text, got = echo_once('best_effort', timeout_s=2.0)
        if got:
            return True
        time.sleep(0.5)
    return False


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if BAG_DIR.exists():
        shutil.rmtree(BAG_DIR)
    stop_children()

    if not topic_has_publisher('/turtle1/pose'):
        write(
            'qos-before.txt',
            'No publisher on /turtle1/pose. Start turtlesim first:\n'
            '  ros2 run turtlesim turtlesim_node\n',
        )
        return 1

    # --- Stage 2: break ---
    start_nodes('reliable', 'before')
    if not wait_topic('/robot_a/sensor_pose'):
        write(
            'qos-before.txt',
            'topic /robot_a/sensor_pose not found\n\n' + diagnose(),
        )
        stop_children()
        return 1
    if not wait_subscription('/turtle1/pose'):
        write(
            'qos-before.txt',
            'pose_relay did not subscribe to /turtle1/pose\n\n' + diagnose(),
        )
        stop_children()
        return 1
    time.sleep(2)
    if not wait_sensor_flow():
        write(
            'qos-before.txt',
            'sensor_pose not delivering with best_effort\n\n' + diagnose(),
        )
        stop_children()
        return 1
    before, got_before = echo_once('reliable', timeout_s=3.0)
    if got_before:
        before = '[UNEXPECTED MESSAGE WITH RELIABLE]\n' + before
    else:
        before = (
            '=== reliable echo against best_effort publisher ===\n'
            'topic visible; no message within timeout (QoS incompatibility)\n'
            + before
        )
    write('qos-before.txt', before)
    stop_children()

    # --- Stage 3: fix on live stream ---
    start_nodes('best_effort', 'after')
    after_parts: list[str] = []
    if not wait_topic('/robot_a/sensor_pose'):
        write('qos-after.txt', 'topic /robot_a/sensor_pose not found\n\n' + diagnose())
        stop_children()
        return 1
    time.sleep(2)
    live, got_live = echo_once('best_effort', timeout_s=5.0)
    after_parts.append('=== live best_effort echo ===\n' + live)
    if not got_live:
        after_parts.append(diagnose())
        write('qos-after.txt', '\n'.join(after_parts))
        stop_children()
        return 1

    if BAG_DIR.exists():
        shutil.rmtree(BAG_DIR)
    # CLI ros2 bag record is flaky under redirected/non-TTY Windows shells.
    # Record with rosbag2_py so metadata.yaml is always finalized.
    print('+ python evidence/pr05/_record_bag.py', flush=True)
    rec = run(
        [
            'python', str(EVIDENCE / '_record_bag.py'),
            '--output', str(BAG_DIR),
            '--topic', '/robot_a/sensor_pose',
            '--seconds', '12',
        ],
        timeout=45,
    )
    after_parts.append(
        '=== bag record ===\n'
        + (rec.stdout or '')
        + (rec.stderr or '')
    )
    stop_children()

    if not (BAG_DIR / 'metadata.yaml').is_file():
        after_parts.append(
            'bag metadata missing after record\n'
            f'bag dir exists={BAG_DIR.exists()}\n'
        )
        write('qos-after.txt', '\n'.join(after_parts))
        return 1

    play_args = [
        'ros2', 'bag', 'play', str(BAG_DIR),
        '--qos-profile-overrides-path',
        str(ROOT / 'config' / 'qos-overrides.yaml'),
        '--disable-keyboard-controls',
    ]

    # Replay pass 1: best_effort must receive (start receiver, then player).
    recv_ok = start_bg(
        [
            'python', str(EVIDENCE / '_recv_once.py'),
            '--reliability', 'best_effort',
            '--timeout', '15',
        ],
        'replay-best.log',
    )
    time.sleep(0.5)
    player = start_bg(play_args, 'play.log')
    try:
        recv_ok.wait(timeout=20)
    except subprocess.TimeoutExpired:
        recv_ok.kill()
    replay_ok_text = ''
    try:
        replay_ok_text = (EVIDENCE / 'replay-best.log').read_text(
            encoding='utf-8', errors='replace'
        )
    except Exception:
        pass
    got_ok = recv_ok.returncode == 0 and (
        'x:' in replay_ok_text.lower() or 'theta:' in replay_ok_text.lower()
    )
    after_parts.append(
        '=== replay best_effort echo ===\n' + replay_ok_text
    )
    if player.poll() is None:
        player.terminate()
        try:
            player.wait(timeout=5)
        except subprocess.TimeoutExpired:
            player.kill()

    # Replay pass 2: reliable must time out against best_effort offer.
    player = start_bg(play_args, 'play2.log')
    time.sleep(0.5)
    replay_bad, got_bad = echo_once('reliable', timeout_s=2.0)
    after_parts.append(
        '=== replay reliable echo (expect no message) ===\n' + replay_bad
    )
    if got_bad:
        after_parts.append('[UNEXPECTED MESSAGE ON RELIABLE REPLAY]\n')
    stop_children()

    info = run(['ros2', 'bag', 'info', str(BAG_DIR)], timeout=30)
    after_parts.append(
        '=== ros2 bag info ===\n' + (info.stdout or info.stderr or '')
    )
    write('qos-after.txt', '\n'.join(after_parts))
    shutil.copy2(BAG_DIR / 'metadata.yaml', EVIDENCE / 'bag-metadata.yaml')
    print('copied bag-metadata.yaml', flush=True)

    if not got_ok:
        print('FAIL: replay best_effort got no message', flush=True)
        return 1
    print('OK', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
