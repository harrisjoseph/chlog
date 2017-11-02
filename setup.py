#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="chlog",
    version='0.1.0',
    description='Changelog update tool using the http://keepachangelog.com/ format',
    author='harrisjoseph',
    packages=find_packages(exclude=['test']),
    package_data={
        '': ['*.rst', '*.md'],
    },
    tests_require=['tox', 'pytest'],
    entry_points={
        'console_scripts': [
            'chlog=chlog.main:main'
        ]
    }
)
