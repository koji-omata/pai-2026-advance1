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
        
        # 1. サブスクライバーとパブリッシャー
        self.image_sub = self.create_subscription(
            Image, '/camera', self.image_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 2. 状態管理変数（ハンチング防止）
        self.arrived = False       # 到達済みフラグ
        self.last_h = 0            # 直前のターゲット高さ[px]
        
        self.get_logger().info('カメラ視覚追従ノード（ハンチング対策版）が起動しました')

    def image_callback(self, msg):
        cmd = Twist()

        # すでに到達している場合は完全停止を維持
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
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 赤色（#FF0000）抽出用マスク
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

            if w > 10 and h > 10:
                self.last_h = h  # 直近の認識サイズを更新
                cx = x + w // 2
                error_x = (width / 2) - cx

                # ① 到達判定（物体の高さが画面の55%を超えたら衝突手前で停止）
                if h > height * 0.55:
                    self.arrived = True
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.0
                    self.get_logger().info(f'【到達完了】ターゲット直前にて完全停止しました！ (高さh: {h}px)')
                else:
                    # ② 直進速度
                    cmd.linear.x = 0.12

                    # ③ 不感帯付きP制御（画面中央から20px以内なら旋回せず直進）
                    if abs(error_x) < 20:
                        cmd.angular.z = 0.0
                    else:
                        cmd.angular.z = 0.0025 * error_x

                    self.get_logger().info(f'【接近中】前進中... 偏差: {int(error_x)}, 高さh: {h}px')
        else:
            # ④ 画角外れセーフティ：直前まで目の前に見えていたのに消えた場合＝近すぎてはみ出たと判定して停止
            if self.last_h > height * 0.4:
                self.arrived = True
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info('【近接到達】ターゲットが画角からはみ出たため直前にて停止しました！')
            else:
                # 本当に見失っている場合のみ回転探索
                cmd.linear.x = 0.0
                cmd.angular.z = 0.25
                self.get_logger().info('【探索中】ターゲットを探して回転中...')

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