from setuptools import find_packages, setup

package_name = 'turtlesim_relative_rotate'

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
            'rotate_relative_pose = turtlesim_relative_rotate.rotate_relative_pose:main',
        ],
    },
)
