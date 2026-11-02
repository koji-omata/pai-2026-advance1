#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class AutoDriver(Node):
    def __init__(self):
        super().__init__('auto_driver')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('AI/自動制御ノードが起動しました')

    def timer_callback(self):
        msg = Twist()
        # ここに判定ロジックや推論結果を入れる
        msg.linear.x = 0.2   # 前進
        msg.angular.z = 0.1  # 緩やかに旋回
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AutoDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
