from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'course_simulation'


def _model_data_files():
    entries = []
    for root, _dirs, files in os.walk('models'):
        if not files:
            continue
        install_dir = os.path.join('share', package_name, root)
        entries.append((install_dir, [os.path.join(root, f) for f in files]))
    return entries


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/worlds', glob('worlds/*')),
        *_model_data_files(),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MiheyPlayGame',
    maintainer_email='81063698+MiheyPlayGame@users.noreply.github.com',
    description='PR07 Gazebo simulation bringup and adapters.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cmd_adapter = course_simulation.cmd_adapter:main',
            'odom_adapter = course_simulation.odom_adapter:main',
        ],
    },
)
