#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class dirvish"""

from backupctl import dirvish


def test_dirvish_config():
    assert dirvish.create_config(
        '/tmp/backupctl/www.example.com',
        'www.example.com',
    )
