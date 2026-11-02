# pai-2026-advance1

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
  /workspace/setup_2drobot.sh
 ```
 YOLOv8を使う場合、セットアップ時にROS 2 Humbleと互換性のあるNumPy 1.xをインストールします。
 すでにNumPy 2.xをインストール済みで上記の`_ARRAY_API not found`エラーが出る場合は、コンテナ内で次を実行してからスクリプトを再実行してください。
 ```
 pip install "numpy<2" ultralytics
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
