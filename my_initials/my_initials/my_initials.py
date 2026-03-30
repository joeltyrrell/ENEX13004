#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn, Kill
from geometry_msgs.msg import Twist
import time
import math

# Custom Class to handle killing, spawning, and moving turtles to draw initials.
class InitialsDrawer(Node):
    def __init__(self):
        super().__init__('initials_drawer') #name of the node
        
        # Service Clients
        self.spawn_cli = self.create_client(Spawn, '/spawn')
        self.kill_cli = self.create_client(Kill, '/kill')

        # Initialise a dictionary to store publsihers for each turtle.
        self.publishers_dict = {}

        # Loop until both services are available
        while not self.spawn_cli.wait_for_service(timeout_sec=1.0) or not self.kill_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for turtlesim services (spawn/kill)...')

    # Function to handle killing a turtle
    def kill_turtle(self, name):
        request = Kill.Request()
        request.name = name
        future = self.kill_cli.call_async(request) # Call the kill service asynchronously
        rclpy.spin_until_future_complete(self, future) # Wait until the service call is complete

    # Function to handle spawning a turtle
    def spawn_turtle(self, x, y, theta, name):
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = name
        future = self.spawn_cli.call_async(request) # Call the spawn service asynchronously
        rclpy.spin_until_future_complete(self, future) # Wait until the service call is complete
        return future.result()

    # Function to handle moving turtle 
    def move_turtle(self, name, linear_x, angular_z, duration):
       
        # Reuse publisher if it exists, otherwise create it
        if name not in self.publishers_dict:
            self.publishers_dict[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', 10)
            time.sleep(0.5)

        # Get the publisher for the turtle and publish the Twist message for the specified duration
        pub = self.publishers_dict[name]
        msg = Twist()
        msg.linear.x = float(linear_x)
        msg.angular.z = float(angular_z)
        
        # Publish the message until the duration has elapsed
        start_time = time.time()
        while time.time() - start_time < duration:
            pub.publish(msg)
            time.sleep(0.0001)
        
        # Stop moving
        pub.publish(Twist())

# Main function
def main(args=None):   
    # Initialize the ROS2 Python client library and create an instance of the InitialsDrawer node
    rclpy.init(args=args)
    node = InitialsDrawer()

    # Kill the initial turtle
    node.get_logger().info('Removing initial turtle')
    node.kill_turtle('turtle1')

    # Spawn turtle J
    node.get_logger().info('Spawning turtle_j')
    node.spawn_turtle(x=4.0, y=9.0, theta=-math.pi/2.0, name='turtle_j')

    # Spawn turtle T
    node.get_logger().info('Spawning turtle_t...')
    node.spawn_turtle(x=8.0, y=2.5, theta=math.pi/2.0, name='turtle_t')

    # Draw J
    node.get_logger().info('Drawing J')
    # Vertical line down
    node.move_turtle('turtle_j', linear_x=1.0, angular_z=0.0, duration=5.0)
    # Curve for the semicircle
    node.move_turtle('turtle_j', linear_x=0.75, angular_z=-0.5, duration=2*math.pi)

    # Draw T
    node.get_logger().info('Drawing T')
    # Vertical line up
    node.move_turtle('turtle_t', linear_x=1.0, angular_z=0.0, duration=6.5)
    # Turn left 90 degrees
    node.move_turtle('turtle_t', linear_x=0.0, angular_z=1.0, duration= math.pi/2)
    # Horizontal line to the left
    node.move_turtle('turtle_t', linear_x=1.0, angular_z=0.0, duration=2.5)
    # Turn left 180 degrees
    node.move_turtle('turtle_t', linear_x=0.0, angular_z=1.0, duration= math.pi)
    # Horizontal line to the right
    node.move_turtle('turtle_t', linear_x=1.0, angular_z=0.0, duration=5.0)
    
    # Cleanup and shutdown
    node.destroy_node()
    rclpy.shutdown()

# Entry point of the script
if __name__ == '__main__':
    main()