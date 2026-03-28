import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerTimer(Node):
    def __init__(self):
        super().__init__('talker_timer')

        # 1) Create a publisher that publishes String messages on the topic /chatter
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # 2) Create a counter so we can see multiple messages
        self.count_ = 0

        # 3) Create a timer that calls self.timer_callback every 0.5 seconds
        timer_period = 0.5  # seconds
        self.timer_ = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info('Talker timer node started. Publishing on /chatter every 0.5s.')

    def timer_callback(self):
        # Create the message
        msg = String()
        msg.data = f'Hello ROS 2! count={self.count_}'

        # Publish the message
        self.publisher_.publish(msg)

        # Log to terminal
        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Increment counter
        self.count_ += 1


def main(args=None):
    rclpy.init(args=args)
    node = TalkerTimer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()