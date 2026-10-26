#!/usr/bin/env bash
set -eo pipefail
# ROS setup.bash references optional unset vars; do not enable nounset here.
source /opt/ros/${ROS_DISTRO}/setup.bash
if [[ -f /ws/install/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /ws/install/setup.bash
fi
export GZ_SIM_RESOURCE_PATH="/ws/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
exec "$@"
