#!/usr/bin/env bash
# Build + headless smoke inside the container (cwd /ws).
set -euo pipefail
source /opt/ros/${ROS_DISTRO}/setup.bash
cd /ws
colcon build --symlink-install --packages-up-to course_simulation
source install/setup.bash
export GZ_SIM_RESOURCE_PATH="$PWD/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
gz sdf -k src/course_simulation/models/course_ackermann/model.sdf
python3 -m pytest src/course_simulation/test -q
mkdir -p evidence/pr07 fixtures
echo "OK: build and unit tests passed. Start launch manually:"
echo "  ros2 launch course_simulation simulation.launch.py headless:=true 2>&1 | tee evidence/pr07/headless.txt"
