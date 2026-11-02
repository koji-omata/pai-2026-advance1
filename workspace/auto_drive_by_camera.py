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
        
        self.get_logger().info('カメラ認識制御ノードが起動しました')

    def image_callback(self, msg):
        try:
            # ROS 2の画像メッセージをOpenCV画像形式に変換
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'画像変換エラー: {e}')
            return

        # --- 認識・制御ロジックの例 ---
        # 画像のサイズ取得 (例: 640x480)
        height, width, _ = cv_image.shape
        
        cmd = Twist()
        # 基本姿勢：ゆっくり前進
        cmd.linear.x = 0.1
        cmd.angular.z = 0.0
        
        # 速度指令をロボットに送信
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
