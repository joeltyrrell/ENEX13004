#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

import math


class RotateRelative(Node):

    def __init__(self):
        super().__init__('rotate_relative')

        self.current_theta = None
        self.target_theta = None
        self.rotating = False

        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

    def rotate(self, relative_angle):

        if self.current_theta is None:
            self.get_logger().warn('Pose not received yet')
            return

        self.target_theta = self.normalize_angle(
            self.current_theta + relative_angle
        )

        self.rotating = True

        self.get_logger().info(
            f'Rotate by {math.degrees(relative_angle):.1f} degrees'
        )

    def pose_callback(self, msg):
        self.current_theta = msg.theta

    def normalize_angle(self, angle):

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        return angle

    def rotate_step(self):

        if not self.rotating or self.current_theta is None:
            return

        error = self.normalize_angle(
            self.target_theta - self.current_theta
        )

        twist = Twist()

        if abs(error) > 0.01:
            twist.angular.z = 1.0
        else:
            twist.angular.z = 0.0
            self.rotating = False
            self.get_logger().info('Rotation completed')

        self.cmd_pub.publish(twist)


def main(args=None):

    rclpy.init(args=args)

    node = RotateRelative()

    # Set the desired relative rotation
    desired_angle = math.radians(90)

    # Wait until pose data is received
    while rclpy.ok() and node.current_theta is None:
        rclpy.spin_once(node)

    # Start rotation
    node.rotate(desired_angle)

    # Poll pose until rotation is complete
    while rclpy.ok() and node.rotating:
        rclpy.spin_once(node)
        node.rotate_step()

    rclpy.shutdown()


if __name__ == '__main__':
    main()