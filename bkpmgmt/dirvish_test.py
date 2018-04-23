#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class dirvish"""

from bkpmgmt import dirvish


def test_dirvish_config():
    assert dirvish.create_config(
        '/tmp/bkpmgmt/www.example.com',
        'www.example.com',
    )
