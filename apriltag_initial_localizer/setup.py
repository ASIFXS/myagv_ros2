from setuptools import setup
import os
from glob import glob

package_name = 'apriltag_initial_localizer'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Asif Ali',
    maintainer_email='mguasifali@gmail.com',
    description='AprilTag-based automatic initial localization for AMCL',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'initial_localizer_node = apriltag_initial_localizer.initial_localizer_node:main'
        ],
    },
)