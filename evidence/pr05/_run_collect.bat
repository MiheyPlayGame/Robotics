@echo off
setlocal
cd /d C:\ROS\ros2-windows
call local_setup.bat
set ROS_DOMAIN_ID=16
cd /d C:\Users\MPG\NSU\Robotics
call install\setup.bat

echo.
echo Keep turtlesim running in the other terminal.
echo Checking /turtle1/pose ...
ros2 topic info /turtle1/pose
if errorlevel 1 (
  echo ERROR: start turtlesim first: ros2 run turtlesim turtlesim_node
  pause
  exit /b 1
)

echo.
echo === PR05 evidence collect ===
python evidence\pr05\_collect.py
echo exit=%ERRORLEVEL%
pause
