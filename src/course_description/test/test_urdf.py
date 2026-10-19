# Copyright 2026 MiheyPlayGame

"""Structural checks for vehicle.urdf.xacro."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import xacro

URDF_XACRO = (
    Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'
)


def _process(mappings: dict[str, str] | None = None) -> ET.Element:
    doc = xacro.process_file(str(URDF_XACRO), mappings=mappings or {})
    return ET.fromstring(doc.toxml())


def _joint(root: ET.Element, name: str) -> ET.Element:
    for joint in root.findall('joint'):
        if joint.get('name') == name:
            return joint
    raise AssertionError(f'joint {name!r} not found')


def test_xacro_expands() -> None:
    root = _process()
    assert root.tag == 'robot'
    assert root.get('name') == 'course_ackermann'


def test_required_links_present() -> None:
    root = _process()
    names = {link.get('name') for link in root.findall('link')}
    for required in ('base_link', 'camera_link', 'lidar_link', 'imu_link'):
        assert required in names


def test_lidar_parent_is_base_link() -> None:
    """Geometry contract: lidar_link must hang off base_link, not camera_link."""
    root = _process()
    joint = _joint(root, 'lidar_joint')
    parent = joint.find('parent')
    assert parent is not None
    assert parent.get('link') == 'base_link'


def test_defect_lidar_parent_camera_link() -> None:
    """Defect mapping: lidar under camera_link (wrong geometry)."""
    root = _process(mappings={'lidar_parent': 'camera_link'})
    joint = _joint(root, 'lidar_joint')
    parent = joint.find('parent')
    assert parent is not None
    assert parent.get('link') == 'camera_link'
    assert parent.get('link') != 'base_link'


def test_fixed_sensor_joints() -> None:
    root = _process()
    for name in ('camera_joint', 'lidar_joint', 'imu_joint'):
        joint = _joint(root, name)
        assert joint.get('type') == 'fixed'


def test_parameters_not_magic_in_source() -> None:
    text = URDF_XACRO.read_text(encoding='utf-8')
    assert 'xacro:property name="wheel_radius"' in text
    assert 'xacro:property name="track"' in text
    assert 'xacro:property name="wheel_base"' in text
    assert 'xacro:property name="base_length"' in text
