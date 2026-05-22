import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('servebot_description')
    gazebo_ros_share = get_package_share_directory('gazebo_ros')

    robot_description = ParameterValue(
        Command(['xacro ', os.path.join(pkg_share, 'urdf', 'servebot.xacro')]),
        value_type=str,
    )

    # Launch Gazebo empty world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')
        ),
    )

    # Publish robot description so spawn_entity and controllers can find it
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # Spawn robot into Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'servebot',
        ],
        output='screen',
    )

    # Load controllers after Gazebo has started (small delay for safety)
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    load_diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        TimerAction(
            period=3.0,
            actions=[load_joint_state_broadcaster, load_diff_drive_controller],
        ),
    ])
