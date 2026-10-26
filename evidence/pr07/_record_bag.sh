#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/lyrical/setup.bash
source /ws/install/setup.bash
export ROS_DOMAIN_ID=16
cd /ws
rm -rf fixtures/pr07-sensors

python3 evidence/pr07/_drive_source.py >/tmp/drive_src.log 2>&1 &
drive_pid=$!

ros2 bag record --storage mcap --use-sim-time -o fixtures/pr07-sensors \
  --topics /vehicle/camera/image_raw /vehicle/scan /vehicle/imu /vehicle/odom \
  /tf /tf_static /clock >/tmp/bag_record.log 2>&1 &
bag_pid=$!

# Wall clock ~45s; with RTF~1 this is enough sim-time. If slow, increase.
sleep 50
kill -INT "$bag_pid" 2>/dev/null || true
# Wait for clean shutdown / metadata write
for _ in $(seq 1 30); do
  if [[ -f fixtures/pr07-sensors/metadata.yaml ]]; then
    break
  fi
  sleep 1
done
kill -TERM "$bag_pid" 2>/dev/null || true
wait "$bag_pid" 2>/dev/null || true
kill "$drive_pid" 2>/dev/null || true
wait "$drive_pid" 2>/dev/null || true

ls -la fixtures/pr07-sensors || true
ros2 bag info fixtures/pr07-sensors | tee evidence/pr07/bag-info.txt
