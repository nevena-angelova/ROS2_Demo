import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Bool


class MoveNode(Node):
    """
    This node is responsible for controlling the robot motion.
    It publishes velocity commands to /cmd_vel and listens for
    obstacle detection messages on /obstacle_detected.
    """

    def __init__(self):
        # Initialize the ROS 2 node with the name 'move_forward_node'
        super().__init__('move_forward_node')

        # Create a publisher that sends velocity commands to the /cmd_vel topic.
        self.publisher_ = self.create_publisher(
            TwistStamped,
            '/cmd_vel',
            10  # QoS queue size
        )

        # Create a subscriber to the /obstacle_detected topic.
        self.subscription = self.create_subscription(
            Bool,
            '/obstacle_detected',
            self.obstacle_callback,  # Callback function executed on message reception
            10
        )

        # Create a timer that triggers the publish_command() method
        # every 0.1 seconds (10 Hz). Timers are used in ROS 2 to run
        # periodic tasks without blocking the node.
        self.timer = self.create_timer(0.1, self.publish_command)

        # Internal state variable updated by the obstacle subscriber
        self.obstacle = False

    def obstacle_callback(self, msg):
        """
        Callback function executed whenever a message is received
        on the /obstacle_detected topic.
        """

        self.obstacle = msg.data

        if self.obstacle:
            self.get_logger().info(
                'Obstacle detected! Adjusting robot motion.'
            )

    def publish_command(self):
        """
        Periodic function that publishes velocity commands to the robot.
        The behavior depends on whether an obstacle is detected.
        """

        msg = TwistStamped()

        # Set the reference coordinate frame of the velocity command
        msg.header.frame_id = 'base_link'

        # Attach the current ROS time to the message
        msg.header.stamp = self.get_clock().now().to_msg()

        if self.obstacle:
            # If an obstacle is detected:
            # Move forward slowly and rotate to avoid the obstacle
            msg.twist.linear.x = 0.02     # forward velocity (m/s)
            msg.twist.angular.z = 0.5    # rotational velocity (rad/s)
        else:
            # If no obstacle is detected:
            # Move forward faster with a slight turn
            msg.twist.linear.x = 0.09
            msg.twist.angular.z = 0.3

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Cmd: linear.x={msg.twist.linear.x:.2f}, '
            f'angular.z={msg.twist.angular.z:.2f}'
        )


def main(args=None):
    """
    Main entry point of the ROS 2 node.
    """
    # Initialize the ROS 2 Python client library
    rclpy.init(args=args)

    node = MoveNode()

    # Keep the node running and processing callbacks
    rclpy.spin(node)

    # Cleanup once the node is stopped
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
