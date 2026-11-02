# pai-2026-advance1

Gazebo上の2輪ロボット移動

*Youtube Link: https://youtube.com/shorts/nqT46Or6Wdw?feature=share
*report: 説明資料_PAI最終課題_omnicampus_omata.pdf

##Environment: WSL2

1.Docker start up (in the WSL2)
 > make
 and access to "localhost 6080"

2.Start up gazebo (in the container)
 > /workspace/2drobot.sh
 > source .bashrc

3.Start up nodes
 For wheel control
 > /workspace/ros2_bridge_wheel.sh
 For camera
 > /workspace/ros2_bridge_camera.sh

3.Control
 By teleope
  > /workspace/ros2_teleope.sh
 By camera
  > /workspace/camera_tracker.py

4.Etc
 Test scripts
 > auto_drive*.py
