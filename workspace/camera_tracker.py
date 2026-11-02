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
        
        # カメラトピックの受信用 (Subscriber)
        self.image_sub = self.create_subscription(
            Image, '/camera', self.image_callback, 10)
        
        # ロボット制御トピックの送信用 (Publisher)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('カメラ視覚追従ノードが起動しました')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'画像変換エラー: {e}')
            return

        height, width, _ = cv_image.shape
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # 赤色オブジェクトのHSV範囲定義（赤色の球体・箱などを想定）
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        moments = cv2.moments(mask)
        cmd = Twist()

        # デバッグ用：現在の検出面積をログ出力
        area = moments['m00']
        
        if area > 500:  # 赤色が視界に入っている場合
            cx = int(moments['m10'] / area)
            error_x = (width / 2) - cx

            # P制御（画面中央を向くように旋回）
            cmd.angular.z = 0.003 * error_x

            # 【変更点】到達判定の閾値を220,000（画面の約7割）に引き上げ
            if area > 220000:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info(f'【到達】ターゲット直前に到着しました！ (面積: {int(area)})')
            else:
                cmd.linear.x = 0.15  # 追従前進
                self.get_logger().info(f'【追従中】前進中... 偏差: {error_x}, 面積: {int(area)}')
        else:
            # 視界に入っていない場合は探索旋回
            cmd.linear.x = 0.0
            cmd.angular.z = 0.3
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
    