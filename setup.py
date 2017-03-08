#!/usr/bin/python
import os.path

from setuptools import setup, find_packages
from dist_utils import fetch_requirements
from dist_utils import apply_vagrant_workaround

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, 'requirements.txt')

install_reqs, dep_links = fetch_requirements(REQUIREMENTS_FILE)


apply_vagrant_workaround()
setup(
    name='counsel',
    version='0.1.1',
    description='CLI utility for Consul',
    author='Denis Baryshev',
    author_email='dennybaa@gmail.com',
    install_requires=install_reqs,
    dependency_links=dep_links,
    packages=find_packages(exclude=['setuptools', 'tests']),
    include_package_data=True,
    license="MIT",
    url='https://github.com/stackfeed/counsel',
    entry_points={
        'console_scripts': [
            'counsel = counsel.cli.main:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Stable',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)
