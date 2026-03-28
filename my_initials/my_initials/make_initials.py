#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from geometry_msgs.msg import Twist
import time
import math

class InitialsDrawer(Node):
    def __init__(self):
        super().__init__('initials_drawer')
        
        # Service Clients
        self.spawn_cli = self.create_client(Spawn, '/spawn')
        self.kill_cli = self.create_client(Kill, '/kill')
        # Dictionary to store and reuse publishers to prevent lag
        self.publishers_dict = {}

        while not self.spawn_cli.wait_for_service(timeout_sec=1.0) or not self.kill_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for turtlesim services (spawn/kill)...')

    # Function to handle killing a turtle
    def kill_turtle(self, name):
        request = Kill.Request()
        request.name = name
        future = self.kill_cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)

    # Function to handle spawning a turtle
    def spawn_turtle(self, x, y, theta, name):
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = name
        future = self.spawn_cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    # Function to Handle moving turtle t
    def move_turtle(self, name, linear_x, angular_z, duration):
        # Reuse publisher if it exists, otherwise create it
        if name not in self.publishers_dict:
            self.publishers_dict[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', 10)
            time.sleep(0.5) # Only sleep once per turtle
        pub = self.publishers_dict[name]
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            pub.publish(msg)
            time.sleep(0.05) # 20Hz: Smoother for VMs, reduces CPU overhead
        
        # Stop moving
        pub.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = InitialsDrawer()

    # 1. Kill the default turtle to clear the canvas
    node.get_logger().info('Removing default turtle...')
    node.kill_turtle('turtle1')

    # 2. Spawn turtle for 'J' (Starting top-left of the letter)
    node.get_logger().info('Spawning turtle_j...')
    node.spawn_turtle(x=4.0, y=9.0, theta=-math.pi/2.0, name='turtle_j')

    # 3. Spawn turtle for 'T' (Starting top-left of the letter)
    node.get_logger().info('Spawning turtle_t...')
    node.spawn_turtle(x=8.0, y=2.5, theta=math.pi/2.0, name='turtle_t')

    # 4. Draw 'J'
    node.get_logger().info('Drawing J...')
    # Vertical line down
    node.move_turtle('turtle_j', linear_x=1.0, angular_z=0.0, duration=5.0)
    # Curve for the hook (positive angular_z turns left/up)
    node.move_turtle('turtle_j', linear_x=0.75, angular_z=-0.5, duration=2*math.pi)

    # 5. Draw 'T'
    node.get_logger().info('Drawing T...')
    # Vertical line up
    node.move_turtle('turtle_t', linear_x=1.0, angular_z=0.0, duration=5.0) # Up to (8,9)
    # ?
    node.move_turtle('turtle_t', linear_x=0.0, angular_z=-1, duration= math.pi)
    node.move_turtle('turtle_t', linear_x=2.5, angular_z=0.0, duration=1.0)
    

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()