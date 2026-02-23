"""
Setup script for Endfield Market Tracker
"""

from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='endfield-market-tracker',
    version='1.0.0',
    author='Endfield Market Tracker Team',
    description='Smart trading companion for Endfield',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/endfield-market-tracker',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: Microsoft :: Windows',
    ],
    entry_points={
        'console_scripts': [
            'endfield-tracker=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.png', '*.jpg', '*.json', '*.db'],
    },
)# Tests module