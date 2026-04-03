from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    package_path = os.path.expanduser('~/ros2_ws/src/robotic_manip_3')
    urdf_file = os.path.join(package_path, 'urdf/robotic_manip_3.urdf')
    rviz_config_file = os.path.join(package_path, 'rviz/view_robot.rviz')

    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}]
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config_file]
        )
    ])