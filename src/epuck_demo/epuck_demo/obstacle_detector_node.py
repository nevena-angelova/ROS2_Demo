import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from sensor_msgs.msg import Range


class ObstacleDetectorNode(Node):
    """
    This node detects obstacles in front of the robot using IR sensors.
    It publishes a Bool message on /obstacle_detected to indicate
    if there is an obstacle.
    """

    def __init__(self):
        # Initialize ROS 2 node with a obstacle_detector_node name
        super().__init__('obstacle_detector_node')

        # Create a publisher to send obstacle detection status
        # to the /obstacle_detected topic
        self.publisher_ = self.create_publisher(Bool, '/obstacle_detected', 10)

        # Initialize an array to store the readings from 8 IR sensors
        self.sensors = [0.0] * 8

        # Subscribe to each of the 8 IR sensor topics
        # Each topic publishes Range messages containing distance measurements
        for i in range(8):
            topic_name = f'/ps{i}'
            self.create_subscription(
                Range,
                topic_name,
                self.make_sensor_callback(i),
                10 # QoS queue size
            )

        # Create a timer that runs check_sensors() periodically (10 Hz)
        self.timer = self.create_timer(0.1, self.check_sensors)

    def make_sensor_callback(self, index):
        """
        Factory function to create a callback for each sensor.
        Stores the latest range reading in self.sensors.
        """
        def callback(msg: Range):
            self.sensors[index] = msg.range
            self.get_logger().info(f'Sensor {index}: {msg.range:.3f}')
        return callback

    def check_sensors(self):
        """
        Check the readings of the front sensors and determine
        if an obstacle is present. Publish the result as a Bool message.
        """

        front_sensors = [self.sensors[0], self.sensors[1],
                         self.sensors[6], self.sensors[7]]

        # Determine if the minimum distance is below the threshold (4 cm)
        obstacle = min(front_sensors) < 0.04

        msg = Bool()
        msg.data = obstacle
        self.publisher_.publish(msg)

        if obstacle:
            self.get_logger().info('Obstacle detected!')
        else:
            self.get_logger().info('Path clear.')


def main(args=None):
    """
    Main entry point of the node
    """
    # Initialize ROS 2 Python client library
    rclpy.init(args=args)

    node = ObstacleDetectorNode()

    # Keep the node alive and processing callbacks
    rclpy.spin(node)

    # Destroy the node and shutdown ROS 2 when finished
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
