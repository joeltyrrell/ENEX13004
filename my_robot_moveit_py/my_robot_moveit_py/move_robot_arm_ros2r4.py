#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Pose
from moveit_msgs.action import MoveGroup, ExecuteTrajectory
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    PlanningOptions,
)
from moveit_msgs.srv import GetCartesianPath

class MoveToPosition(Node):
    def __init__(self):
        super().__init__('move_arm_position')
        
        # Initialise MoveGroup - move robot from random position to start position
        self._move_client = ActionClient(self, MoveGroup, 'move_action')
        self.get_logger().info('Waiting for move_action server...')
        self._move_client.wait_for_server()
        self.get_logger().info('Connected to move_action')

        # Initialise GetCartesianPath - Striaght line path between letter points
        self._cartesian_client = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.get_logger().info('Waiting for compute_cartesian_path service...')
        self._cartesian_client.wait_for_service()
        self.get_logger().info('Connected to compute_cartesian_path')

        # Initialise ActionClient - segment arm movement
        self._execute_client = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        self.get_logger().info('Waiting for execute_trajectory server...')
        self._execute_client.wait_for_server()
        self.get_logger().info('Connected to execute_trajectory')
            
        # Track which point of letter the script is up to
        self.letterposition = 0
                
        # Coordinates of letter points
        self.letterpoints = [
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  # Apex
            {'x': 0.534, 'y':  0.25, 'z': 0.100},  # Bottom Right
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  # Back to Apex
            {'x': 0.534, 'y': -0.25, 'z': 0.100},  # Bottom Left
            {'x': 0.534, 'y': -0.15, 'z': 0.472},  # Crossbar Left
            {'x': 0.534, 'y':  0.15, 'z': 0.472}   # Crossbar Right
        ]

    #Create pose message with horizontal EE orientation and position of letter point.
    def create_pose(self, lp):
        p = Pose()
        p.position.x = lp['x']
        p.position.y = lp['y']
        p.position.z = lp['z']
        
        # Fixed quaternion rotation
        p.orientation.x = 0.0
        p.orientation.y = 0.7071
        p.orientation.z = 0.0
        p.orientation.w = 0.7071
        return p
    
    #Check if goal was accepted and if so, wait for result. If not, shutdown node.
    def action_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return rclpy.shutdown()

        self.get_logger().info('Goal accepted')
        goal_handle.get_result_async().add_done_callback(self.action_result_callback)

    #Check if action succeeded and if so, execute next task. If not, shutdown node.
    def action_result_callback(self, future):
        result = future.result().result
        # MoveIt error code 1 = Pass
        if result.error_code.val == 1:
            self.get_logger().info('Action successful.')
            if self.next_task:
                self.next_task()
        else:
            self.get_logger().error(f"Action failed code: {result.error_code.val}")
            rclpy.shutdown()

    #Use MoveGroup action to move robot from any random position to the apex of letter A, done with joint constraints to ensure robot start pose is consistent.
    def move_to_start(self):
        self.get_logger().info('Moving to Initial Position...')
        
        goal_msg = MoveGroup.Goal()
        request = MotionPlanRequest()
        request.group_name = 'arm'
        request.max_velocity_scaling_factor = 0.5
        
        # Define target joint angles for the A Apex position
        joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        joint_values = [0.0, 0.0, 0.7854, 0.0, 0.7854, 0.0] 
        
        # Create joint contraints
        constraints = Constraints()
        for i in range(6):
            jc = JointConstraint()
            jc.joint_name = joint_names[i]
            jc.position = joint_values[i]
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        # Set the goal constraints to the joint constraints defined above    
        request.goal_constraints = [constraints]
        goal_msg.request = request
        goal_msg.planning_options = PlanningOptions()

        # On successful completion of this move, start the preview of the letter path. 
        self.next_task = self.start_preview
        future = self._move_client.send_goal_async(goal_msg)
        future.add_done_callback(self.action_response_callback)

    # Show Robot arm trail for total letter
    def start_preview(self):

        self.get_logger().info('Computing Letter trail...')
        
        # Create a Cartesian path request with all letter points as waypoints to show the full trail. 
        req = GetCartesianPath.Request()
        req.header.frame_id = 'base_link'
        req.group_name = 'arm'
        req.max_step = 0.02 # Resolution of the calculated line
        
        for lp in self.letterpoints:
            req.waypoints.append(self.create_pose(lp))

        # Asynchronously call the service to update RViz visuals
        self._cartesian_client.call_async(req)
        
        # 10s delay to allow inspection of the computed path before moving
        self.get_logger().info('Trail Computed, Waiting 10 seconds...')
        self.timer = self.create_timer(10.0, self.send_segment_goal)

    def send_segment_goal(self):
        if self.timer: 
            self.timer.cancel()
            self.timer = None

        if self.letterposition >= len(self.letterpoints):
            self.get_logger().info('Drawing Complete!')
            return rclpy.shutdown()

        self.get_logger().info(f'Moving to corner {self.letterposition}...')
        req = GetCartesianPath.Request(group_name='arm', max_step=0.1)
        req.header.frame_id = 'base_link'
        req.waypoints.append(self.create_pose(self.letterpoints[self.letterposition]))

        self._cartesian_client.call_async(req).add_done_callback(self.exec_segment_cb)

    def exec_segment_cb(self, future):
        # Result from Cartesian path service is used to create the execution goal
        goal_msg = ExecuteTrajectory.Goal(trajectory=future.result().solution)
        self.next_task = self.increment_and_loop
        future = self._execute_client.send_goal_async(goal_msg)
        future.add_done_callback(self.action_response_callback)

    def increment_and_loop(self):
        self.letterposition += 1
        self.send_segment_goal()

def main(args=None):
    rclpy.init(args=args)
    node = MoveToPosition()
    node.move_to_start()
    rclpy.spin(node)

if __name__ == '__main__':
    main()