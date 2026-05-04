#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    PlanningOptions,
)

# Essential services/actions for calculating and following 3D paths
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.action import ExecuteTrajectory

class MoveToPosition(Node):
    def __init__(self):
        super().__init__('move_arm_position')
        
        # Initialize clients to communicate with MoveIt's move_group node
        self._move_client = ActionClient(self, MoveGroup, 'move_action')
        self._cartesian_client = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self._execute_client = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')

        # Ensure all services are active before proceeding
        self._move_client.wait_for_server()
        self._cartesian_client.wait_for_service()
        self._execute_client.wait_for_server()

        self.letterposition = 1  # Track which corner we are currently moving toward
        
        # Define the 3D coordinates for the shape we want to draw
        self.lettercorners = [
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  
            {'x': 0.534, 'y':  0.25, 'z': 0.100},  
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  
            {'x': 0.534, 'y': -0.25, 'z': 0.100},  
            {'x': 0.534, 'y': -0.15, 'z': 0.472},  
            {'x': 0.534, 'y':  0.15, 'z': 0.472}   
        ]

    def create_ps(self, lp):
        """Helper to convert raw coordinates into a MoveIt-ready PoseStamped message."""
        ps = PoseStamped()
        ps.header.frame_id = 'base_link'  # Reference coordinates from the robot's base
        ps.pose.position.x = lp['x']
        ps.pose.position.y = lp['y']
        ps.pose.position.z = lp['z']
        
        # Fixed orientation: Ensures the gripper always points downward
        ps.pose.orientation.x = 0.0
        ps.pose.orientation.y = 0.7071
        ps.pose.orientation.z = 0.0
        ps.pose.orientation.w = 0.7071
        return ps

    # --- PHASE 0: MOVE TO JOINT START ---
    def move_to_start(self):
        """Moves the robot to a known safe starting configuration using joint angles."""
        self.get_logger().info('Phase 0: Moving to Joint Configuration...')
        
        goal_msg = MoveGroup.Goal()
        request = MotionPlanRequest()
        request.group_name = 'arm'
        request.max_velocity_scaling_factor = 0.5
        
        # Specify target angles for each individual joint
        joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        joint_values = [0.0, 0.0, 0.7854, 0.0, 0.7854, 0.0] 
        
        constraints = Constraints()
        for i in range(len(joint_names)):
            jc = JointConstraint()
            jc.joint_name = joint_names[i]
            jc.position = joint_values[i]
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
            
        request.goal_constraints.append(constraints)
        goal_msg.request = request
        goal_msg.planning_options = PlanningOptions()

        # Asynchronously send the goal to prevent blocking the node
        self._move_client.send_goal_async(goal_msg).add_done_callback(self.move_to_start_cb)

    def move_to_start_cb(self, future):
        """Callback to handle the server's acceptance of the joint move goal."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            return rclpy.shutdown()
        # Once accepted, wait for the movement to finish before starting preview
        goal_handle.get_result_async().add_done_callback(self.start_preview)

    # --- PHASE 1: DISPLAY ONLY & TIMER ---
    def start_preview(self, future):
        """Computes the full path and displays it as a trail in RViz."""
        self.get_logger().info('Phase 1: Computing RViz trail...')
        req = GetCartesianPath.Request()
        req.header.frame_id = 'base_link'
        req.group_name = 'arm'
        req.max_step = 0.02  # Interpolate points every 2cm for a smooth path
        
        # Add all corners to the request to visualize the entire shape
        for lp in self.lettercorners:
            req.waypoints.append(self.create_ps(lp).pose)

        self._cartesian_client.call_async(req)
        
        # Start a 10-second timer to give the user time to inspect the trail in RViz
        self.get_logger().info('Trail displayed. Waiting 10 seconds...')
        self.timer = self.create_timer(10.0, self.send_segment_goal)

    # --- PHASE 2: SEGMENT EXECUTION ---
    def send_segment_goal(self):
        """Executes the movement to the next corner in the list."""
        if hasattr(self, 'timer'): 
            self.timer.cancel()  # Stop the timer so it doesn't trigger again

        # If we have reached the last corner, shut down the node
        if self.letterposition >= len(self.lettercorners):
            self.get_logger().info('Drawing Complete!')
            return rclpy.shutdown()

        self.get_logger().info(f'Moving to corner {self.letterposition}...')
        req = GetCartesianPath.Request()
        req.header.frame_id = 'base_link'
        req.group_name = 'arm'
        req.max_step = 0.1
        # Calculate a linear path to the specific target corner
        req.waypoints.append(self.create_ps(self.lettercorners[self.letterposition]).pose)

        self._cartesian_client.call_async(req).add_done_callback(self.exec_segment_cb)

    def exec_segment_cb(self, future):
        """Receives the calculated Cartesian path and sends it for execution."""
        goal_msg = ExecuteTrajectory.Goal()
        goal_msg.trajectory = future.result().solution
        
        # Use a lambda to chain the next segment call after this one completes
        self._execute_client.send_goal_async(goal_msg).add_done_callback(
            lambda f: f.result().get_result_async().add_done_callback(self.next_step)
        )

    def next_step(self, future):
        """Increments the counter and loops back to send the next segment goal."""
        self.letterposition += 1
        self.send_segment_goal()

def main(args=None):
    rclpy.init(args=args)
    node = MoveToPosition()
    node.move_to_start()  # Entry point for the logic chain
    rclpy.spin(node)      # Keep the node alive to process callbacks

if __name__ == '__main__':
    main()