# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A ROS 2 colcon workspace (repo root = workspace root) containing one `ament_python` package, `src/epuck_demo`, that drives an e-puck robot to avoid obstacles using its 8 IR proximity sensors. The `/ps0`–`/ps7` `Range` topics and `/cmd_vel` `TwistStamped` interface match the Webots e-puck driver (`webots_ros2_epuck`), which is not part of this repo and must be launched separately.

## Commands

Run from the repo root with a ROS 2 distro sourced (`source /opt/ros/<distro>/setup.bash`):

```bash
colcon build --packages-select epuck_demo   # add --symlink-install to avoid rebuilding after Python edits
source install/setup.bash
ros2 run epuck_demo obstacle_detector_node
ros2 run epuck_demo move_node
colcon test --packages-select epuck_demo && colcon test-result --verbose
```

There is no launch file; each node is started with its own `ros2 run`. There is no `test/` directory yet, so `colcon test` runs nothing until tests are added. `package.xml` declares `ament_flake8`/`ament_pep257` test deps, so new tests would normally follow the standard ament linter test files. Node executables are registered as `console_scripts` in `setup.py`. Add an entry there for any new node.

## Architecture

Two nodes, connected through one topic:

```
/ps0../ps7 (sensor_msgs/Range) ──> obstacle_detector_node ──/obstacle_detected (std_msgs/Bool)──> move_forward_node ──> /cmd_vel (geometry_msgs/TwistStamped)
```

- `obstacle_detector_node.py`: caches the latest reading per sensor and, on a 10 Hz timer, publishes `True` if any **front** sensor (indices 0, 1, 6, 7) reads < 0.04 m.
- `move_node.py`: the ROS node name is `move_forward_node`, not `move_node`. On a 10 Hz timer it publishes a fixed command: slow forward plus a strong turn when an obstacle is flagged, otherwise faster forward plus a gentle turn.

Points to keep in mind when changing behavior:
- Sensor values start at `0.0`, so the detector reports an obstacle until real readings arrive.
- Both nodes use timers rather than reacting directly in subscriber callbacks. Control output is decoupled from sensor message rate.
- `package.xml` only lists test dependencies. Runtime deps (`rclpy`, `std_msgs`, `sensor_msgs`, `geometry_msgs`) are not declared as `<exec_depend>`, so `rosdep` won't install them.
