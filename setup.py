"""Setuptools package definition."""
# -*- coding: utf-8 -*-

import codecs
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

__version__ = None
version_file = path.join(here, "backupctl", "version.py")
with codecs.open(version_file, encoding="UTF-8") as f:
    code = compile(f.read(), version_file, 'exec')
    exec(code)

with codecs.open('README.rst', 'r', encoding='UTF-8') as f:
    README_TEXT = f.read()

setup(
    name='backupctl',
    version=__version__,
    author='Adfinis SyGroup AG',
    author_email='https://www.adfinis-sygroup.ch/',
    description='Manage dirvish backups with an underlying zfs storage pool.',
    long_description=README_TEXT,
    install_requires=(
        'pyxdg',
        'jinja2',
        'SQLAlchemy',
    ),
    keywords='dirvish, zfs',
    url='https://www.adfinis-sygroup.ch/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: '
        'GNU General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points="""
    [console_scripts]
    backupctl=backupctl.backupctl:main
    backupctl-start=backupctl.backupctl:backup_start
    backupctl-stop=backupctl.backupctl:backup_stop
    """
)
