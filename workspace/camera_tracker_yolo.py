#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class YoloTracker(Node):
    def __init__(self):
        super().__init__('yolo_tracker')
        self.bridge = CvBridge()
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.image_sub = self.create_subscription(
            Image, '/camera', self.image_callback, 10)
        
        # YOLOv8n 事前学習済みAIモデルのロード
        self.model = YOLO('yolov8n.pt')
        self.arrived = False
        self.last_h = 0
        self.get_logger().info('YOLOv8 AI視覚追従ノードが起動しました')

    def image_callback(self, msg):
        cmd = Twist()
        if self.arrived:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'画像変換エラー: {e}')
            return

        height, width, _ = cv_image.shape

        # --- AI（YOLOv8）による推論実行 ---
        # resultsはバッチ単位のリストで返るため [0] で1枚目の結果を取得
        results = self.model(cv_image, conf=0.08, verbose=False)
        boxes = results[0].boxes

        if len(boxes) > 0:
            # 検出された物体の中で最も確信度(conf)が高いものを選択
            best_box = max(boxes, key=lambda b: float(b.conf[0]))
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            cls_id = int(best_box.cls[0])
            cls_name = self.model.names[cls_id]
            conf_val = float(best_box.conf[0])

            w = x2 - x1
            h = y2 - y1
            cx = x1 + w // 2
            error_x = (width / 2) - cx
            self.last_h = h

            # ① 到達判定（AI検出枠の高さhが画面の50%を超えたら衝突手前で完全停止）
            if h > height * 0.50:
                self.arrived = True
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info(f'【AI到達停止】[{cls_name}] (conf:{conf_val:.2f}) 直前で完全停止 (h:{h}px)')
            else:
                cmd.linear.x = 0.12
                # ② 不感帯付きP制御（中央偏差20px以内は直進）
                if abs(error_x) < 20:
                    cmd.angular.z = 0.0
                else:
                    cmd.angular.z = 0.0025 * float(error_x)

                self.get_logger().info(f'【AI追従中】[{cls_name}] (conf:{conf_val:.2f}) 偏差:{int(error_x)}, 高さh:{h}px')
        else:
            # ③ 画角外れセーフティ（直前まで近くに見えていた場合）
            if self.last_h > height * 0.35:
                self.arrived = True
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info('【AI近接到達】ターゲット画角外れのため停止しました！')
            else:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.25
                self.get_logger().info('【AI探索中】YOLOでターゲットを探して回転中...')

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = YoloTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()