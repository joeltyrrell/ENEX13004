#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    PositionConstraint,
    MotionPlanRequest,
    PlanningOptions,
)
from shape_msgs.msg import SolidPrimitive


class MoveToPosition(Node):
    def __init__(self):
        super().__init__('move_arm_position')

        self._action_client = ActionClient(self, MoveGroup, '/move_action')
        self.get_logger().info('Waiting for /move_action server...')
        self._action_client.wait_for_server()
        self.get_logger().info('Connected to /move_action')

    def send_position_goal(self):
        goal_msg = MoveGroup.Goal()

        request = MotionPlanRequest()
        request.group_name = 'arm'
        request.allowed_planning_time = 20.0
        request.num_planning_attempts = 20

        target_pose = PoseStamped()
        target_pose.header.frame_id = 'base_link'

        # Small move from your initial position
        target_pose.pose.position.x = -0.20
        target_pose.pose.position.y = 1.0
        target_pose.pose.position.z = 0.2

        position_constraint = PositionConstraint()
        position_constraint.header = target_pose.header
        position_constraint.link_name = 'link_ee'

        region = SolidPrimitive()
        region.type = SolidPrimitive.BOX
        region.dimensions = [0.05, 0.05, 0.05]

        position_constraint.constraint_region.primitives.append(region)
        position_constraint.constraint_region.primitive_poses.append(target_pose.pose)
        position_constraint.weight = 1.0

        constraints = Constraints()
        constraints.position_constraints.append(position_constraint)

        request.goal_constraints = [constraints]
        goal_msg.request = request
        goal_msg.planning_options = PlanningOptions()

        self.get_logger().info(
            f"Sending position-only goal to "
            f"x={target_pose.pose.position.x}, "
            f"y={target_pose.pose.position.y}, "
            f"z={target_pose.pose.position.z}"
        )

        future = self._action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Result error code: {result.error_code.val}")
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = MoveToPosition()
    node.send_position_goal()
    rclpy.spin(node)


if __name__ == '__main__':
    main()