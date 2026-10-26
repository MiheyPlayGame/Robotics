# Launch an interactive PR07 container with the repo mounted at /ws.
# Requires Docker Desktop. Example:
#   .\docker\run-pr07.ps1
#   docker exec -it robotics-pr07 bash

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Error "docker not found. Install Docker Desktop, then re-open the terminal."
}

docker build -f "$Repo\docker\Dockerfile.pr07" -t robotics-pr07 "$Repo"

$existing = docker ps -aq -f name=robotics-pr07
if ($existing) {
  docker rm -f robotics-pr07 | Out-Null
}

# Docker Desktop on Windows: no --network host; stay on bridge + ROS_DOMAIN_ID.
docker run -d --name robotics-pr07 `
  -e ROS_DOMAIN_ID=16 `
  -v "${Repo}:/ws" `
  robotics-pr07 `
  sleep infinity

Write-Host "Container robotics-pr07 is up. Enter with:"
Write-Host "  docker exec -it robotics-pr07 bash"
Write-Host "Then:"
Write-Host "  colcon build --symlink-install --packages-up-to course_simulation"
Write-Host "  source install/setup.bash"
Write-Host "  ros2 launch course_simulation simulation.launch.py headless:=true"
