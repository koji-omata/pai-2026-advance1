# pai-2026-advance1

## 提出物　(最終締め切り後更新)
* Youtube Link: https://youtube.com/shorts/nqT46Or6Wdw?feature=share
* レポート: 説明資料_PAI最終課題_omnicampus_omata.pdf

## 概要
### テーマ： Gazebo上の2輪ロボット移動
### 開発環境：WSL2

## 使い方

1. Docker start up (in the WSL2)
 ```
 cd ~/pai-2026-advance1
 make
 ```
 その後ブラウザで "localhost:6080"　にアクセス

2. Start up gazebo (in the container)
 コンテナ内のCUIでセットアップ
 ```
  /workspace/2drobot.sh
  source .bashrc
 ```

3. Start up ROS2 nodes
 - For wheel control
 ```
 /workspace/ros2_bridge_wheel.sh
 ```
 - For camera
 ```
 /workspace/ros2_bridge_camera.sh
 ```
4. Control tools
 - By teleope
  ```
  /workspace/ros2_teleope.sh
  ```
 - By camera
  ```
  /workspace/camera_tracker.py
  ```
5. Etc
 - Test scripts
 ```
 auto_drive*.py
 ```
