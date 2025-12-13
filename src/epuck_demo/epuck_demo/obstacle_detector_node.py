import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from sensor_msgs.msg import Range

class ObstacleDetectorNode(Node):
    def __init__(self):
        super().__init__('obstacle_detector_node')

        # Publisher за obstacle
        self.publisher_ = self.create_publisher(Bool, '/obstacle_detected', 10)

        # IR sensor array
        self.sensors = [0.0]*8

        # Subscriber-и to IR sensors
        for i in range(8):
            topic_name = f'/ps{i}'
            self.create_subscription(
                Range,
                topic_name,
                self.make_sensor_callback(i),
                10
            )

        self.timer = self.create_timer(0.1, self.check_sensors)

    def make_sensor_callback(self, index):
        def callback(msg: Range):
            self.sensors[index] = msg.range
            self.get_logger().info(f'Sensor {index}: {msg.range:.3f}')
        return callback

    def check_sensors(self):
        front_sensors = [self.sensors[0], self.sensors[1], self.sensors[6], self.sensors[7]]
        obstacle = min(front_sensors) < 0.04  # threshold 4 cm

        msg = Bool()
        msg.data = obstacle
        self.publisher_.publish(msg)

        if obstacle:
            self.get_logger().info('Obstacle detected!')
        else:
            self.get_logger().info('Path clear.')

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
