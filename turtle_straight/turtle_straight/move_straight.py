
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class MoveStraight(Node):

    def __init__(self):
        super().__init__('move_straight_node')

        # Parameters
        self.declare_parameter('speed', 1.0)
        self.declare_parameter('distance', 2.0)

        self.speed = float(self.get_parameter('speed').value)
        self.target_distance = float(self.get_parameter('distance').value)

        # Publisher
        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Subscriber
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # State variables
        self.start_x = None
        self.start_y = None
        self.current_pose = None

        # Timer (20 Hz control loop)
        self.timer = self.create_timer(0.05, self.move)

        self.get_logger().info(
            f"Speed: {self.speed}, Distance: {self.target_distance}"
        )

    def pose_callback(self, msg):
        self.current_pose = msg

        if self.start_x is None:
            self.start_x = msg.x
            self.start_y = msg.y

    def move(self):

        if self.current_pose is None:
            return

        distance_moved = math.hypot(
            self.current_pose.x - self.start_x,
            self.current_pose.y - self.start_y
        )

        twist = Twist()

        if distance_moved < self.target_distance:
            twist.linear.x = self.speed
        else:
            twist.linear.x = 0.0
            self.publisher_.publish(twist)
            self.get_logger().info("Target reached. Stopping.")
            rclpy.shutdown()
            return

        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = MoveStraight()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()