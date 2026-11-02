source /opt/ros/humble/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
  /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist \
  /camera@sensor_msgs/msg/Image[ignition.msgs.Image
  
