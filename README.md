# 🤖 Physical AI 応用講座 最終課題：YOLOv8 視覚追従自律走行ロボット

東京大学 松尾・岩澤研究室「Physical AI 応用講座」の最終課題リポジトリです。
Gazebo Sim (Ignition) 上の差動二輪ロボットに搭載した単眼 RGB カメラから画像トピックを取得し、**YOLOv8（深層学習物体検出 AI）** によるリアルタイム推論と画像フィードバック制御（P 制御）を用いて、ターゲット（コーラ缶）を自動で探索・アプローチし、衝突直前でピタッと安全停止するシステムを構築しました。

---

## 📽️ デモ動画

- **YouTube Shorts (1分動画)**: https://www.youtube.com/shorts/hWyN7LgINFY
*(回転探索 ➔ YOLOv8 による物体検出 ➔ 高精度アプローチ ➔ 衝突手前での完全停止の様子を収録)*

---

## 🌟 主な特徴・工夫点

1. **YOLOv8 事前学習済み AI モデルの統合 (`yolov8n.pt`)**
   - 単色の簡易色抽出ではなく、COCO データセットで事前学習された `ultralytics YOLOv8` を ROS 2 ノード内でリアルタイム推論。
   - `bottle` / `cup` クラス（コーラ缶）を高確信度（conf > 0.80）で識別。

2. **不感帯 (Deadband) 付き P 制御**
   - 画面中心からの偏差 ($error_x$) に応じた比例制御を導入。
   - 中央 +-20 px に不感帯を設定することで、直進中の首振り・蛇行動作（バタつき）を防止。

3. **バウンディングボックス高さ比率による衝突直前停止**
   - LiDAR や Depth センサを使わず、AI 検出枠の高さ比率 ($h / height > 50%$) を距離指標として活用。
   - ターゲットの数十 cm 手前（衝突直前）でピタッと完全停止する安定アプローチを実現。

4. **ハンチング・画角外れ防止セーフティメカニズム**
   - **到達状態保持 (`self.arrived`)**: 到達判定後は完全停止を維持し、探索へ逆戻りするハンチングを遮断。
   - **画角外れセーフティ (`self.last_h`)**: ターゲットに大接近して画面上部からはみ出た場合も近接到達と判定して停止。

---

## 🏗️ システム構成 & 技術スタック

```text
+-----------------------------------------------------------------------+
|  Gazebo Sim (World / Robot / Camera Sensor / Coke Can Target)        |
+-----------------------------------------------------------------------+
                                   │
              (gz.msgs.Image)      │      (gz.msgs.Twist)
                                   ▼
+-----------------------------------------------------------------------+
|  ros_gz_bridge (parameter_bridge)                                     |
|   - /camera  : sensor_msgs/msg/Image                                 |
|   - /cmd_vel : geometry_msgs/msg/Twist                               |
+-----------------------------------------------------------------------+
                                   │
             (sensor_msgs/Image)   │      (geometry_msgs/Twist)
                                   ▼
+-----------------------------------------------------------------------+
|  ROS 2 Humble Node (camera_tracker_yolo.py)                            |
|   - Ultralytics YOLOv8 (yolov8n.pt)  <-- AI 推論                    |
|   - Image Feedback P-Control + Deadband                              |
|   - Bounding Box Safety Stop Logic                                    |
+-----------------------------------------------------------------------+
```

| コンポーネント | 仕様 / ツール |
| :--- | :--- |
| **OS / 開発環境** | Windows + WSL2 + Docker (`compose.yaml`) |
| **ミドルウェア** | ROS 2 Humble |
| **シミュレータ** | Gazebo Sim / Ignition Gazebo (`world.sdf`) |
| **メッセージブリッジ** | `ros_gz_bridge` (`ros2 run ros_gz_bridge parameter_bridge`) |
| **AI モデル** | Ultralytics YOLOv8 Nano (`yolov8n.pt`) |
| **画像処理** | OpenCV, `cv_bridge` |

---

## 📂 リポジトリ構成

```text
.
├── camera_tracker_yolo.py    # YOLOv8 AI 視覚追従 ROS 2 ノード (主プログラム)
├── world.sdf                 # カメラ付き二輪ロボット & Coke Can ターゲット配置 SDF
├── compose.yaml              # 開発環境コンテナ定義ファイル
├── ros2_bridge_camera.sh     # ROS 2 <-> Gazebo 画像トピックブリッジ起動スクリプト
├── ros2_bridge_cmd_vel.sh    # ROS 2 <-> Gazebo 速度指令トピックブリッジ起動スクリプト
└── README.md                 # 本ドキュメント
```

---

## 🚀 実行手順

### 1. 依存ライブラリの準備
Docker コンテナ内で Python 依存パッケージをセットアップします。
```bash
pip install ultralytics opencv-python numpy
```

### 2. Gazebo シミュレーションの起動
`world.sdf` を指定して Gazebo ワールドを起動します。
```bash
ign gazebo world.sdf
# または
gz sim world.sdf
```

### 3. ROS 2 <-> Gazebo メッセージブリッジの起動
カメラ画像トピックと速度指令トピックのブリッジを接続します。
```bash
# カメラ画像ブリッジ
ros2 run ros_gz_bridge parameter_bridge /camera@sensor_msgs/msg/Image[gz.msgs.Image

# 制御指令ブリッジ
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

### 4. YOLOv8 AI 追従ノードの実行
別ターミナルで AI 追従ノードを起動します。
```bash
python3 camera_tracker_yolo.py
```
ロボットが回転探索を行い、ターゲット（コーラ缶）を AI 認識すると自動でアプローチを開始し、直前で安全停止します。

---

## 🔗 参考 & 謝辞

- **ベースラインリポジトリ**: [OsawaKousei / 2DRoboPrac_ws](https://github.com/OsawaKousei/2DRoboPrac_ws)
  *（差動二輪ロボットの基本ワールド構成モデル `world.sdf` を参考に拡張いたしました）*
- **講座情報**: 東京大学 松尾・岩澤研究室 Physical AI 応用講座 (2026)
- **Omnicampus ID**: `KojiOmata`
