import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtlesim.action import RotateAbsolute


class RotateAbsoluteClient(Node):

    def __init__(self):
        super().__init__('rotate_absolute_client')

        # Parameter for the target orientation in radians
        self.declare_parameter('theta', 1.57)
        self.target_theta = float(self.get_parameter('theta').value)

        # Create the action client
        self._action_client = ActionClient(
            self,
            RotateAbsolute,
            '/turtle1/rotate_absolute'
        )

        self.get_logger().info(
            f'Waiting for action server /turtle1/rotate_absolute...'
        )
        self._action_client.wait_for_server()

        self.send_goal(self.target_theta)

    def send_goal(self, theta):
        goal_msg = RotateAbsolute.Goal()
        goal_msg.theta = float(theta)

        self.get_logger().info(
            f'Sending goal: rotate turtle to {theta:.2f} rad'
        )

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted.')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        remaining = feedback_msg.feedback.remaining
        self.get_logger().info(
            f'Remaining angle: {remaining:.3f} rad'
        )

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(
            f'Rotation finished. Delta moved: {result.delta:.3f} rad'
        )
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = RotateAbsoluteClient()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()