#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener, TransformException


class RobotTransformListener(Node):

    def __init__(self):
        super().__init__('robot_tf_listener')

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer = self.create_timer(0.1, self.lookup_transform)

    def lookup_transform(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                'base_link',
                'link_ee',
                rclpy.time.Time()
            )

            x = transform.transform.translation.x
            y = transform.transform.translation.y
            z = transform.transform.translation.z

            self.get_logger().info(
                f'End-effector position: x={x:.2f}, y={y:.2f}, z={z:.2f}'
            )

        except TransformException as ex:
            self.get_logger().warn(str(ex))


def main(args=None):
    rclpy.init(args=args)
    node = RobotTransformListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()