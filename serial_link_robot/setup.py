from setuptools import find_packages, setup

package_name = 'serial_link_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/joint_publisher.launch.py']),
        ('share/' + package_name + '/urdf', ['urdf/serial_link_robot.urdf']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Serial link robot joint publisher tutorial package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'joint_publisher = serial_link_robot.joint_publisher:main',
            'random_joint_publisher = serial_link_robot.random_joint_publisher:main',
            'robot_transform = serial_link_robot.robot_transform: main',
        ],
    },
)