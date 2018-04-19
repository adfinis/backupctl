#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class zfs"""

from bkpmgmt import zfs


def test_new_zfs_filesystem():
    assert zfs.new_filesystem(
        'backup/bkpmgmt-test1',
        '/tmp/bkpmgmt-test1',
        '10M',
        compression=True,
    )


def test_resize_zfs_filesystem():
    assert zfs.resize_filesystem(
        'backup/bkpmgmt-test1',
        '20M',
    )


def test_remove_zfs_filesystem():
    assert zfs.remove_filesystem(
        'backup/bkpmgmt-test1',
    )
