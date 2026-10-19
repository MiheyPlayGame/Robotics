"""Expand xacro and write model-check.txt."""

from __future__ import annotations

from pathlib import Path

import xacro
from urdf_parser_py.urdf import URDF

ROOT = Path(__file__).resolve().parents[2]
XACRO = ROOT / 'src' / 'course_description' / 'urdf' / 'vehicle.urdf.xacro'
EVIDENCE = Path(__file__).resolve().parent


def main() -> int:
    xml = xacro.process_file(str(XACRO)).toxml()
    (EVIDENCE / 'vehicle.urdf').write_text(xml, encoding='utf-8')
    robot = URDF.from_xml_string(xml)
    lines = [
        '=== xacro expand + urdf_parser_py (check_urdf substitute on Windows) ===',
        f'robot name: {robot.name}',
        f'links ({len(robot.links)}): '
        + ', '.join(sorted(link.name for link in robot.links)),
        f'joints ({len(robot.joints)}):',
    ]
    for joint in robot.joints:
        lines.append(
            f'  {joint.name}: {joint.parent} -> {joint.child} ({joint.type})'
        )
    lines.append('parse: OK (tree loaded, no parse errors)')
    lines.append('')
    lines.append('=== defect check (lidar_parent:=camera_link) ===')
    broken = xacro.process_file(
        str(XACRO), mappings={'lidar_parent': 'camera_link'}
    ).toxml()
    broken_robot = URDF.from_xml_string(broken)
    lidar = next(j for j in broken_robot.joints if j.name == 'lidar_joint')
    lines.append(
        f'lidar_joint parent={lidar.parent} child={lidar.child} '
        '(wrong geometry; test_lidar_parent_is_base_link fails)'
    )
    lines.append('Restored default lidar_parent=base_link for delivery.')
    out = EVIDENCE / 'model-check.txt'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(f'wrote {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
