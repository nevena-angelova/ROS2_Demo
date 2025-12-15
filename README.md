ROS2 Demo is a simple robot control project built with ROS 2. It demonstrates obstacle detection and autonomous movement using IR sensors. The system consists of two main nodes:

ObstacleDetectorNode – Reads 8 IR sensors and publishes a Bool message when an obstacle is detected in front of the robot.

MoveNode – Subscribes to the obstacle detection topic and commands the robot to move forward or turn to avoid obstacles using velocity commands (/cmd_vel).

The project showcases ROS 2 concepts such as nodes, publishers, subscribers, timers, and message passing for real-time robot navigation.