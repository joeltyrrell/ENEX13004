#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn


class SpawnTurtleClient(Node):

    def __init__(self):
        super().__init__('spawn_turtle_client')

        self.client = self.create_client(Spawn, '/spawn')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

    def send_request(self, x, y, theta, name):

        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = name

        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main(args=None):

    rclpy.init(args=args)

    node = SpawnTurtleClient()

    # Set the new turtle pose and name here
    x = 5.0
    y = 2.0
    theta = 0.0
    name = 'turtle2'

    response = node.send_request(x, y, theta, name)

    if response is not None:
        node.get_logger().info(f'New turtle created: {response.name}')
    else:
        node.get_logger().error('Service call failed')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()