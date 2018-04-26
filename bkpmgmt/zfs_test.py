#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class zfs"""

import pytest

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


@pytest.mark.xfail
def test_resize_zfs_filesystem_too_small():
    assert zfs.resize_filesystem(
        'backup/bkpmgmt-test1',
        '1',
    )


def test_fs_usage():
    assert zfs.filesystem_usage('backup/bkpmgmt-test1') < 1024 * 1024


def test_remove_zfs_filesystem():
    assert zfs.remove_filesystem(
        'backup/bkpmgmt-test1',
    )


def test_parse_size():
    assert zfs.parse_size('1B') == 1
    assert zfs.parse_size('10k') == 10240
    assert zfs.parse_size('400M') == 419430400
    assert zfs.parse_size('11G') == 11811160064
    assert zfs.parse_size('1T') == 1099511627776
