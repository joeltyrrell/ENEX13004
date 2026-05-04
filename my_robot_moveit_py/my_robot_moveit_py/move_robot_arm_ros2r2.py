#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Pose
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.action import ExecuteTrajectory, MoveGroup
from moveit_msgs.msg import (
    Constraints, 
    JointConstraint,
    MotionPlanRequest, 
    PlanningOptions
)

class MoveToPosition(Node):
    def __init__(self):
        super().__init__('move_arm_position')

        # Action Clients
        self._move_client = ActionClient(self, MoveGroup, 'move_action')
        self._cartesian_client = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self._execute_client = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        
        self.get_logger().info('Waiting for MoveIt services...')
        self._move_client.wait_for_server()
        self._cartesian_client.wait_for_service()
        self._execute_client.wait_for_server()
        self.get_logger().info('Connected!')

        # --- CONFIGURATION ---
        self.step_size = 0.1  
        self.speed = 0.1       
        self.display_step_multiplier = 0.2  
        
        self.lettercorners = [
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  
            {'x': 0.534, 'y':  0.25, 'z': 0.100},  
            {'x': 0.534, 'y':  0.00, 'z': 1.030},  
            {'x': 0.534, 'y': -0.25, 'z': 0.100},  
            {'x': 0.534, 'y': -0.15, 'z': 0.472},  
            {'x': 0.534, 'y':  0.15, 'z': 0.472}   
        ]
        self.letterposition = 0

    def create_pose(self, lp):
        pose = Pose()
        pose.position.x = lp['x']
        pose.position.y = lp['y']
        pose.position.z = lp['z']
        pose.orientation.x = 0.0
        pose.orientation.y = 0.7071
        pose.orientation.z = 0.0
        pose.orientation.w = 0.7071
        return pose

    # ==========================================
    # PHASE 0: MOVE TO JOINT CONFIGURATION
    # ==========================================
    def move_to_start(self):
        self.get_logger().info('Phase 0: Moving to specific Joint Configuration...')
        
        goal_msg = MoveGroup.Goal()
        req = MotionPlanRequest()
        req.group_name = 'arm'
        req.max_velocity_scaling_factor = self.speed
        req.max_acceleration_scaling_factor = self.speed
        
        joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        target_joints = [0.0, 0.0, 0.7854, 0.0, 0.7854, 0.0] 
        
        constraints = Constraints()
        for name, val in zip(joint_names, target_joints):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = val
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
            
        req.goal_constraints.append(constraints)
        goal_msg.request = req
        goal_msg.planning_options = PlanningOptions()

        future = self._move_client.send_goal_async(goal_msg)
        future.add_done_callback(self.approach_goal_cb)

    def approach_goal_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Joint goal rejected')
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.approach_result_cb)

    def approach_result_cb(self, future):
        result = future.result().result
        if result.error_code.val == 1:
            self.get_logger().info('Success! At joint start. Calculating trail...')
            self.display_full_shape() 
        else:
            self.get_logger().error(f'Phase 0 failed: {result.error_code.val}')
            rclpy.shutdown()

    # ==========================================
    # PHASE 1: DISPLAY ONLY
    # ==========================================
    def display_full_shape(self):
        req = GetCartesianPath.Request()
        req.header.frame_id = 'base_link'
        req.group_name = 'arm'
        req.max_step = self.step_size * self.display_step_multiplier
        
        for lp in self.lettercorners:
            req.waypoints.append(self.create_pose(lp))

        self.get_logger().info('Phase 1: Computing RViz trail...')
        future = self._cartesian_client.call_async(req)
        future.add_done_callback(self.display_response_cb)

    def display_response_cb(self, future):
        result = future.result()
        if result.fraction < 0.95:
            self.get_logger().error(f'Trail calculation failed: {result.fraction}')
            rclpy.shutdown()
            return
        
        self.get_logger().info('Trail displayed. Waiting 10 seconds...')
        self.delay_timer = self.create_timer(10.0, self.start_segments) 

    # ==========================================
    # PHASE 2: SEGMENT EXECUTION
    # ==========================================
    def start_segments(self):
        self.delay_timer.cancel()
        self.get_logger().info('Phase 2: Drawing segments...')
        self.letterposition = 1  # Starting from Index 1 as Index 0 was the start
        self.send_segment_goal()

    def send_segment_goal(self):
        if self.letterposition >= len(self.lettercorners):
            self.get_logger().info('Drawing Complete! Shutting down...')
            rclpy.shutdown()
            return
            
        req = GetCartesianPath.Request()
        req.header.frame_id = 'base_link'
        req.group_name = 'arm'
        req.max_step = self.step_size
        req.max_velocity_scaling_factor = self.speed
        req.max_acceleration_scaling_factor = self.speed
        req.waypoints.append(self.create_pose(self.lettercorners[self.letterposition]))

        future = self._cartesian_client.call_async(req)
        future.add_done_callback(self.segment_cartesian_cb)

    def segment_cartesian_cb(self, future):
        result = future.result()
        if result.fraction < 0.95:
            self.get_logger().error('Segment planning failed.')
            rclpy.shutdown()
            return
        goal_msg = ExecuteTrajectory.Goal()
        goal_msg.trajectory = result.solution
        self._execute_client.send_goal_async(goal_msg).add_done_callback(self.segment_exec_cb)

    def segment_exec_cb(self, future):
        future.result().get_result_async().add_done_callback(self.segment_result_cb)

    def segment_result_cb(self, future):
        result = future.result().result
        if result.error_code.val == 1:
            self.letterposition += 1
            self.send_segment_goal()
        else:
            self.get_logger().error(f"Execution Error: {result.error_code.val}")
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = MoveToPosition()
    try:
        node.move_to_start() 
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()