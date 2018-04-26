#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class zfs"""

import pytest

from bkpmgmt import zfs

mock_data = {
    'zfs-create':   (0, '', ''),
    'zfs-resize':   (0, '', ''),
    'zfs-destroy':  (0, '', ''),
    'zfs-get':      (0, '0', ''),
    'zfs-set':      (0, '', ''),
}


@pytest.fixture()
def mock_zfs(mocker):
    commands = []

    def mocked(cmd):
        commands.append(cmd)
        return mock_data['-'.join(cmd[:2])]
    mocker.patch('bkpmgmt.zfs.execute_cmd', mocked)
    yield commands


def test_new_zfs_filesystem(mock_zfs):
    zfs.new_filesystem(
        'backup/bkpmgmt-test1',
        '/tmp/bkpmgmt-test1',
        '10M',
        compression=True,
    )


def test_resize_zfs_filesystem(mock_zfs):
    assert zfs.resize_filesystem(
        'backup/bkpmgmt-test1',
        '20M',
    )


@pytest.mark.xfail
def test_resize_zfs_filesystem_too_small(mock_zfs):
    assert zfs.resize_filesystem(
        'backup/bkpmgmt-test1',
        '1',
    )


def test_fs_usage(mock_zfs):
    assert zfs.filesystem_usage('backup/bkpmgmt-test1') == 0


def test_remove_zfs_filesystem(mock_zfs):
    assert zfs.remove_filesystem(
        'backup/bkpmgmt-test1',
    )


def test_parse_size():
    assert zfs.parse_size('1B') == 1
    assert zfs.parse_size('10k') == 10240
    assert zfs.parse_size('400M') == 419430400
    assert zfs.parse_size('11G') == 11811160064
    assert zfs.parse_size('1T') == 1099511627776
