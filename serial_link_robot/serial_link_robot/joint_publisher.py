#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


class JointPublisher(Node):
    def __init__(self):
        super().__init__('robot_joint_publisher')

        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)

        self.timer = self.create_timer(0.1, self.publish_joint_angles)

        self.joint_state_msg = JointState()
        self.joint_state_msg.name = ['joint_1', 'joint_2', 'joint_3']
        self.joint_state_msg.position = [0.5, 0.5, 1.2]
        self.joint_state_msg.velocity = []
        self.joint_state_msg.effort = []

    def publish_joint_angles(self):
        self.joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher_.publish(self.joint_state_msg)


def main(args=None):
    rclpy.init(args=args)
    node = JointPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()