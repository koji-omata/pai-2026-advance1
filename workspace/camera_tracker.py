#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraTracker(Node):
    def __init__(self):
        super().__init__('camera_tracker')
        self.bridge = CvBridge()
        
        # 1. カメラトピックの受信用 (Subscriber)
        self.image_sub = self.create_subscription(
            Image, '/camera', self.image_callback, 10)
        
        # 2. ロボット制御トピックの送信用 (Publisher)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('カメラ視覚追従ノードが起動しました')

    def image_callback(self, msg):
        try:
            # ROS 2の画像メッセージをOpenCV形式(BGR)に変換
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'画像変換エラー: {e}')
            return

        height, width, _ = cv_image.shape
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # ----------------------------------------------------
        # ① 赤色ターゲット（#FF0000）抽出用マスク作成
        # ----------------------------------------------------
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2  # 赤色部分のマスク画像

        # ----------------------------------------------------
        # ② 輪郭（コントゥア）の検出と位置計算
        # ----------------------------------------------------
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cmd = Twist()

        if contours:
            # 画面内で一番大きな赤色領域を取得
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

            # ノイズ除去（幅と高さが一定以上の領域のみ処理）
            if w > 10 and h > 10:
                # 物体の中心座標X
                cx = x + w // 2
                error_x = (width / 2) - cx

                # P制御（画面中央に向くように旋回）
                cmd.angular.z = 0.003 * error_x

                # ----------------------------------------------------
                # ③ 到達判定（物体の高さhが画面高さの65%を超えたら衝突直前で停止）
                # ----------------------------------------------------
                if h > height * 0.65:
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.0
                    self.get_logger().info(f'【到達】ターゲットの目の前で停止しました！ (高さh: {h}px)')
                else:
                    cmd.linear.x = 0.15  # 接近前進
                    self.get_logger().info(f'【接近中】前進中... 偏差: {int(error_x)}, 高さh: {h}px / {height}px')
        else:
            # 画面内に赤色が見つからない場合は回転して探す
            cmd.linear.x = 0.0
            cmd.angular.z = 0.3
            self.get_logger().info('【探索中】ターゲットを探して回転中...')

        # 速度指令を送信
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = CameraTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()