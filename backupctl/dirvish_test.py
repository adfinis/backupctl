#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Test for class dirvish"""

import os

import sqlalchemy

from backupctl.dirvish import Dirvish

BACKUPCTL_DB = os.path.join(
    os.sep,
    'tmp',
    'backupctl',
    'backupctl.db',
)


def test_dirvish_config():
    if not os.path.exists(os.path.dirname(BACKUPCTL_DB)):
        os.makedirs(os.path.dirname(BACKUPCTL_DB))
    engine = sqlalchemy.create_engine('sqlite:///{0}'.format(BACKUPCTL_DB))
    dirvish = Dirvish(engine)
    assert dirvish.create_config(
        os.path.join(
            os.sep,
            'tmp',
            'backupctl',
            'dirvish',
        ),
        'example',
        'www.example.com',
        'www.example.com',
    )


def test_create_machine():
    if not os.path.exists(os.path.dirname(BACKUPCTL_DB)):
        os.makedirs(os.path.dirname(BACKUPCTL_DB))
    engine = sqlalchemy.create_engine('sqlite:///{0}'.format(BACKUPCTL_DB))
    dirvish = Dirvish(engine)
    dirvish.create_machine(
        'backup.example.com',
        'client.example.com',
    )


def test_dirvish_start():
    if not os.path.exists(os.path.dirname(BACKUPCTL_DB)):
        os.makedirs(os.path.dirname(BACKUPCTL_DB))
    engine = sqlalchemy.create_engine('sqlite:///{0}'.format(BACKUPCTL_DB))
    dirvish = Dirvish(engine)
    os.environ['DIRVISH_SRC'] = ''
    os.environ['DIRVISH_IMAGE'] = 'client.example.com:default:1970-01-01_00:00'
    os.environ['DIRVISH_DEST'] = '/backup/client.example.com/latest/tree'
    os.environ['DIRVISH_EXCLUDE'] = '/backup/client.example.com/latest/exclude'
    os.environ['DIRVISH_CLIENT'] = 'client.example.com'
    os.environ['DIRVISH_SERVER'] = 'backup.example.com'
    dirvish.backup_start()


def test_dirvish_stop():
    if not os.path.exists(os.path.dirname(BACKUPCTL_DB)):
        os.makedirs(os.path.dirname(BACKUPCTL_DB))
    engine = sqlalchemy.create_engine('sqlite:///{0}'.format(BACKUPCTL_DB))
    dirvish = Dirvish(engine)
    os.environ['DIRVISH_STATUS'] = 'success'
    os.environ['DIRVISH_SRC'] = ''
    os.environ['DIRVISH_IMAGE'] = 'client.example.com:default:1970-01-01_00:00'
    os.environ['DIRVISH_DEST'] = '/backup/client.example.com/latest/tree'
    os.environ['DIRVISH_EXCLUDE'] = '/backup/client.example.com/latest/exclude'
    os.environ['DIRVISH_CLIENT'] = 'client.example.com'
    os.environ['DIRVISH_SERVER'] = 'backup.example.com'
    dirvish.backup_stop()
