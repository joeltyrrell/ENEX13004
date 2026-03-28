from setuptools import find_packages, setup

package_name = 'turtle_control_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROSIndustrial',
    maintainer_email='ROSIndustrial@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'move_straight = turtle_straight.move_straight:main',
        'turtle_vel_pub = turtle_control_pkg.turtle_vel_pub:main',
        'turtle_move_distance_pose = turtle_control_pkg.turtle_move_distance_pose:main',
    ],
},
)
