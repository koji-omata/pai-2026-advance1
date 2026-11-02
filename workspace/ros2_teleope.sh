source /opt/ros/humble/setup.bash

# ROS 2から前進の速度指令トピックを発行
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"