from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robotic_manip_3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*.urdf')),

        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='Serial link robot URDF',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [],
    },
)