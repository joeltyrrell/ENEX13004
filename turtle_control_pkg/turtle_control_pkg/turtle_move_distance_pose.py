import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class TurtleMoveDistancePose(Node):
    def __init__(self):
        super().__init__('turtle_move_distance_pose')

        # Publisher: send velocity commands
        self.cmd_pub_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Subscriber: receive pose feedback
        self.pose_sub_ = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # Timer: control loop rate (10 Hz)
        self.dt_ = 0.1
        self.timer_ = self.create_timer(self.dt_, self.control_loop)

        # Motion parameters
        self.speed_ = 2.0          # forward speed (turtlesim units/s)
        self.target_dist_ = 5.0    # target travel distance (turtlesim units)

        # Pose tracking
        self.have_start_pose_ = False
        self.start_x_ = 0.0
        self.start_y_ = 0.0
        self.current_x_ = 0.0
        self.current_y_ = 0.0

        # State
        self.done_ = False

        self.get_logger().info(
            f'Started turtle_move_distance_pose: moving forward {self.target_dist_} units using /turtle1/pose feedback.'
        )

    def pose_callback(self, msg: Pose):
        # Save current pose
        self.current_x_ = msg.x
        self.current_y_ = msg.y

        # Capture start pose once (first received pose)
        if not self.have_start_pose_:
            self.start_x_ = msg.x
            self.start_y_ = msg.y
            self.have_start_pose_ = True
            self.get_logger().info(f'Start pose captured at x={self.start_x_:.2f}, y={self.start_y_:.2f}')

    def traveled_distance(self) -> float:
        # Euclidean distance from start pose to current pose
        dx = self.current_x_ - self.start_x_
        dy = self.current_y_ - self.start_y_
        return math.sqrt(dx * dx + dy * dy)

    def stop_turtle(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_pub_.publish(msg)

    def control_loop(self):
        # Wait until we have pose feedback
        if not self.have_start_pose_:
            return

        if self.done_:
            # Ensure turtle stays stopped
            self.stop_turtle()
            return

        dist = self.traveled_distance()

        if dist < self.target_dist_:
            cmd = Twist()
            cmd.linear.x = self.speed_
            cmd.angular.z = 0.3  # straight line
            self.cmd_pub_.publish(cmd)
            self.get_logger().info(f'Distance: {dist:.2f}/{self.target_dist_:.2f}')
        else:
            self.stop_turtle()
            self.done_ = True
            self.get_logger().info(f'Target reached: {dist:.2f} units. Stopping turtle.')
            # Optional: stop timer to reduce logging/CPU
            self.timer_.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = TurtleMoveDistancePose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()