import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleVelPublisher(Node):
    def __init__(self):
        super().__init__('turtle_vel_pub')

        # Publish Twist messages to control turtle velocity
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Publish at 10 Hz
        self.timer_period_ = 0.05  # seconds
        self.timer_ = self.create_timer(self.timer_period_, self.timer_callback)

        self.get_logger().info('turtle_vel_pub started: publishing to /turtle1/cmd_vel at 10 Hz')

    def timer_callback(self):
        msg = Twist()

        # Linear velocity (forward speed) in m/s (turtlesim units)
        msg.linear.x = 3.0

        # Angular velocity (turning) in rad/s
        msg.angular.z = 1.7

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleVelPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()