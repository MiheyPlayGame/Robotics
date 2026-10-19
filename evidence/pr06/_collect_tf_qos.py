"""Collect /tf_static QoS evidence while robot_state_publisher is running."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
DOMAIN = os.environ.get('ROS_DOMAIN_ID', '16')


def env() -> dict[str, str]:
    e = os.environ.copy()
    e['ROS_DOMAIN_ID'] = DOMAIN
    return e


def run(args: list[str], timeout: float = 30) -> subprocess.CompletedProcess[str]:
    print('+', ' '.join(args), flush=True)
    return subprocess.run(
        args,
        cwd=str(ROOT),
        env=env(),
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def main() -> int:
    # Clean leftover publishers
    subprocess.run(
        [
            'powershell', '-NoProfile', '-Command',
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.CommandLine -match "
            "'robot_state_publisher|display.launch' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force "
            "-ErrorAction SilentlyContinue }",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    time.sleep(1)

    log = open(EVIDENCE / 'rsp.log', 'w', encoding='utf-8', errors='replace')
    launch = subprocess.Popen(
        ['ros2', 'launch', 'course_description', 'display.launch.py'],
        cwd=str(ROOT),
        env=env(),
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            topics = run(['ros2', 'topic', 'list'], timeout=10)
            if '/tf_static' in (topics.stdout or '').splitlines():
                break
            if launch.poll() is not None:
                print('FAIL: launch exited early', flush=True)
                print(Path(EVIDENCE / 'rsp.log').read_text(encoding='utf-8', errors='replace'))
                return 1
            time.sleep(1)
        else:
            print('FAIL: /tf_static not found', flush=True)
            return 1

        time.sleep(2)
        parts: list[str] = ['## topic info /tf_static\n']
        info = run(['ros2', 'topic', 'info', '/tf_static', '--verbose'], timeout=15)
        parts.append((info.stdout or '') + (info.stderr or ''))

        parts.append('\n## echo transient_local\n')
        tl = run(
            [
                'python', str(EVIDENCE / '_recv_tf_static.py'),
                '--durability', 'transient_local',
                '--timeout', '5',
            ],
            timeout=20,
        )
        parts.append((tl.stdout or '') + (tl.stderr or ''))
        parts.append(f'exit={tl.returncode}\n')

        parts.append('\n## echo volatile\n')
        vol = run(
            [
                'python', str(EVIDENCE / '_recv_tf_static.py'),
                '--durability', 'volatile',
                '--timeout', '4',
            ],
            timeout=20,
        )
        parts.append((vol.stdout or '') + (vol.stderr or ''))
        parts.append(f'exit={vol.returncode}\n')

        parts.append(
            '\n## notes\n'
            '`/tf_static` uses RELIABLE + TRANSIENT_LOCAL so a late subscriber '
            'still receives the last fixed transforms (camera/lidar/imu).\n'
            '`/tf` is VOLATILE: it carries moving frames and does not keep history '
            'for late joiners. That matches static mounts vs dynamic joints/odom.\n'
        )

        out = EVIDENCE / 'tf-qos.txt'
        out.write_text(''.join(parts), encoding='utf-8', newline='\n')
        print(f'wrote {out}', flush=True)

        if tl.returncode != 0:
            print('FAIL: transient_local did not receive', flush=True)
            return 1
        if vol.returncode == 0:
            print('WARN: volatile unexpectedly received', flush=True)
        return 0
    finally:
        launch.terminate()
        try:
            launch.wait(timeout=5)
        except subprocess.TimeoutExpired:
            launch.kill()
        log.close()


if __name__ == '__main__':
    sys.exit(main())
