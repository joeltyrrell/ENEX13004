import os
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
from launch_ros.actions import Node  # We need this to add our spawner

def generate_launch_description():
    # Point directly to the basic robot description package
    urdf_path = os.path.join(
        get_package_share_directory("my_robot_description"),
        "urdf",
        "robot.urdf" 
    )

    moveit_config = (
        MoveItConfigsBuilder("robotic_manip_3", package_name="robot_config")
        .robot_description(file_path=urdf_path)
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )
    
    # Grab the default launch sequence
    ld = generate_demo_launch(moveit_config)

    # Force the arm_controller to spawn and activate
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
    )
    
    # Add our forced spawner to the list of things to launch
    ld.add_action(arm_controller_spawner)

    return ld