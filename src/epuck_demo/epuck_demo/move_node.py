import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Bool


class MoveNode(Node):
    def __init__(self):
        super().__init__('move_forward_node')

        # Publisher to /cmd_vel
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        
        # Subscriber to /obstacle_detected
        self.subscription = self.create_subscription(
            Bool,
            '/obstacle_detected',
            self.obstacle_callback,
            10
        )
        # Timer 0.1s (10Hz)
        self.timer = self.create_timer(0.1, self.publish_command)
        self.obstacle = False

    def obstacle_callback(self, msg):
        self.obstacle = msg.data
        if self.obstacle:
            self.get_logger().info('Obstacle detected! Stopping or turning.')

    def publish_command(self):
        msg = TwistStamped()
        msg.header.frame_id = 'base_link'
        msg.header.stamp = self.get_clock().now().to_msg()

        if self.obstacle:
            msg.twist.linear.x = 0.02
            msg.twist.angular.z = 0.5
        else:
            msg.twist.linear.x = 0.09
            msg.twist.angular.z = 0.3

        self.publisher_.publish(msg)
        self.get_logger().info(
            f'Cmd: linear.x={msg.twist.linear.x:.2f}, angular.z={msg.twist.angular.z:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = MoveNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
