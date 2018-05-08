#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class zfs"""

import pytest

from backupctl import zfs

mock_data = {
    'zfs-create':   (0, '',  ''),
    'zfs-resize':   (0, '',  ''),
    'zfs-destroy':  (0, '',  ''),
    'zfs-get':      (0, '0', ''),
    'zfs-set':      (0, '',  ''),
}


@pytest.fixture()
def mock_zfs(mocker):
    commands = []

    def mocked(cmd):
        commands.append(cmd)
        return mock_data['-'.join(cmd[:2])]
    mocker.patch('backupctl.zfs.execute_cmd', mocked)
    yield commands


def test_new_zfs_filesystem(mock_zfs):
    zfs.new_filesystem(
        'backup/backupctl-test1',
        '/tmp/backupctl-test1',
        '10M',
        compression=True,
    )
    assert mock_zfs == [[
        'zfs',
        'create',
        '-o',
        'compression=on',
        '-o',
        'dedup=off',
        '-o',
        'quota=10M',
        '-o',
        'mountpoint=/tmp/backupctl-test1',
        'backup/backupctl-test1',
    ]]


def test_new_zfs_filesystem_no_compression(mock_zfs):
    zfs.new_filesystem(
        'backup/backupctl-test1',
        '/tmp/backupctl-test1',
        '10M',
        compression=False,
    )
    assert mock_zfs == [[
        'zfs',
        'create',
        '-o',
        'compression=off',
        '-o',
        'dedup=off',
        '-o',
        'quota=10M',
        '-o',
        'mountpoint=/tmp/backupctl-test1',
        'backup/backupctl-test1',
    ]]


def test_resize_zfs_filesystem(mock_zfs):
    assert zfs.resize_filesystem(
        'backup/backupctl-test1',
        '20M',
    )
    assert mock_zfs == [
        [
            'zfs',
            'get',
            '-H',
            '-o',
            'value',
            '-p',
            'used',
            'backup/backupctl-test1',
        ],
        [
            'zfs',
            'set',
            'quota=20M',
            'backup/backupctl-test1',
        ],
    ]


@pytest.mark.xfail
def test_resize_zfs_filesystem_too_small(mock_zfs):
    assert zfs.resize_filesystem(
        'backup/backupctl-test1',
        '1',
    )
    assert mock_zfs == [
        [
            'zfs',
            'get',
            '-H',
            '-o',
            'value',
            '-p',
            'used',
            'backup/backupctl-test1',
        ],
        [
            'zfs',
            'set',
            'quota=1',
            'backup/backupctl-test1',
        ],
    ]


def test_fs_usage(mock_zfs):
    assert zfs.filesystem_usage('backup/backupctl-test1') == 0
    assert mock_zfs == [[
        'zfs',
        'get',
        '-H',
        '-o',
        'value',
        '-p',
        'used',
        'backup/backupctl-test1',
    ]]


def test_remove_zfs_filesystem(mock_zfs):
    assert zfs.remove_filesystem(
        'backup/backupctl-test1',
    )
    assert mock_zfs == [
        [
            'zfs',
            'set',
            'mountpoint=none',
            'backup/backupctl-test1',
        ],
        [
            'zfs',
            'destroy',
            '-r',
            '-f',
            'backup/backupctl-test1',
        ],
    ]


@pytest.mark.parametrize("human_size, parsed_bytes", [
    ('1B',      1),
    ('10k',     10240),
    ('400M',    419430400),
    ('11G',     11811160064),
    ('1T',      1099511627776),
])
def test_parse_size(human_size, parsed_bytes):
    assert zfs.parse_size(human_size) == parsed_bytes


def test_execute_cmd():
    zfs.execute_cmd(
        [
            'echo',
            'hello world',
        ],
        communicate=False,
    )
    returncode, stdout, stderr = zfs.execute_cmd([
        'echo',
        'hello world',
    ])
    assert returncode == 0
    assert stdout == "hello world\n"
    assert stderr == ''
