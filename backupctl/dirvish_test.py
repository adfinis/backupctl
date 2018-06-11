#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Test for class dirvish"""

import os

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
    dirvish = Dirvish(BACKUPCTL_DB)
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
