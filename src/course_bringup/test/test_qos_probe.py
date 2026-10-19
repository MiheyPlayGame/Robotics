# Copyright 2026 MiheyPlayGame

"""Unit tests for qos_probe reliability mapping."""

from course_bringup.qos_probe import reliability_from_name
from rclpy.qos import ReliabilityPolicy


def test_reliability_best_effort() -> None:
    assert reliability_from_name('best_effort') == ReliabilityPolicy.BEST_EFFORT
    assert reliability_from_name('BEST-EFFORT') == ReliabilityPolicy.BEST_EFFORT


def test_reliability_reliable() -> None:
    assert reliability_from_name('reliable') == ReliabilityPolicy.RELIABLE


def test_reliability_rejects_unknown() -> None:
    try:
        reliability_from_name('volatile')
        raise AssertionError('expected ValueError')
    except ValueError as error:
        assert 'unsupported reliability' in str(error)
