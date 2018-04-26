#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class bkpmgmt"""

import pytest

from bkpmgmt import bkpmgmt, history


@pytest.fixture(autouse=True)
def hist():
    hist_obj = history.History('/tmp/bkpmgmt.db')
    return hist_obj


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


def test_customer(mock_zfs):
    bkpmgmt.new(
        hist(),
        pool='backup',
        root='/tmp/backup',
        customer='customer1',
        size='1G',
        client=None,
    )
    bkpmgmt.resize(
        hist(),
        pool='backup',
        customer='customer1',
        size='2G',
    )
    bkpmgmt.remove(
        hist(),
        pool='backup',
        customer='customer1',
    )
    assert mock_zfs == [
        [
            'zfs',
            'create',
            '-o',
            'compression=on',
            '-o',
            'dedup=off',
            '-o',
            'quota=1G',
            '-o',
            'mountpoint=/srv/backup/customer1',
            'backup/customer1',
        ],
        [
            'zfs',
            'get',
            '-H',
            '-o',
            'value',
            '-p',
            'used',
            'backup/customer1',
        ],
        [
            'zfs',
            'set',
            'quota=2G',
            'backup/customer1',
        ],
        [
            'zfs',
            'set',
            'mountpoint=none',
            'backup/customer1',
        ],
        [
            'zfs',
            'destroy',
            '-r',
            '-f',
            'backup/customer1',
        ],
    ]


def test_vault(mock_zfs):
    bkpmgmt.new(
        hist(),
        pool='backup',
        root='/tmp/backup',
        customer='customer1',
        size='1G',
        client=None,
    )
    bkpmgmt.new(
        hist(),
        pool='backup',
        root='/tmp/backup',
        customer='customer1',
        vault='www.example.com',
        size='500M',
        client=None,
    )
    bkpmgmt.new(
        hist(),
        pool='backup',
        root='/tmp/backup',
        customer='customer1',
        vault='mail.example.com',
        size='500M',
        client='192.0.2.1',
    )
    bkpmgmt.resize(
        hist(),
        pool='backup',
        customer='customer1',
        vault='mail.example.com',
        size='200M',
    )
    bkpmgmt.remove(
        hist(),
        pool='backup',
        customer='customer1',
        vault='mail.example.com',
    )
    bkpmgmt.remove(
        hist(),
        pool='backup',
        customer='customer1',
    )
    assert mock_zfs == [
        [
            'zfs',
            'create',
            '-o',
            'compression=on',
            '-o',
            'dedup=off',
            '-o',
            'quota=1G',
            '-o',
            'mountpoint=/srv/backup/customer1',
            'backup/customer1',
        ],
        [
            'zfs',
            'create',
            '-o',
            'compression=on',
            '-o',
            'dedup=off',
            '-o',
            'quota=500M',
            '-o',
            'mountpoint=/srv/backup/customer1/www.example.com',
            'backup/customer1/www.example.com',
        ],
        [
            'zfs',
            'create',
            '-o',
            'compression=on',
            '-o',
            'dedup=off',
            '-o',
            'quota=500M',
            '-o',
            'mountpoint=/srv/backup/customer1/mail.example.com',
            'backup/customer1/mail.example.com',
        ],
        [
            'zfs',
            'get',
            '-H',
            '-o',
            'value',
            '-p',
            'used',
            'backup/customer1/mail.example.com',
        ],
        [
            'zfs',
            'set',
            'quota=200M',
            'backup/customer1/mail.example.com',
        ],
        [
            'zfs',
            'set',
            'mountpoint=none',
            'backup/customer1/mail.example.com',
        ],
        [
            'zfs',
            'destroy',
            '-r',
            '-f',
            'backup/customer1/mail.example.com',
        ],
        [
            'zfs',
            'set',
            'mountpoint=none',
            'backup/customer1',
        ],
        [
            'zfs',
            'destroy',
            '-r',
            '-f',
            'backup/customer1',
        ],
    ]


@pytest.mark.xfail
def test_new_no_customer():
    bkpmgmt.new(
        hist(),
        customer=None,
        vault=None,
        size=None,
        client=None,
    )


@pytest.mark.xfail
def test_new_no_vault_or_size():
    bkpmgmt.new(
        hist(),
        customer='customer1',
        vault=None,
        size=None,
        client=None,
    )


@pytest.mark.xfail
def test_resize_no_customer():
    bkpmgmt.resize(
        hist(),
        customer=None,
        vault=None,
        size=None,
    )


@pytest.mark.xfail
def test_resize_no_size():
    bkpmgmt.resize(
        hist(),
        customer='customer1',
        vault=None,
        size=None,
    )


@pytest.mark.xfail
def test_remove_no_customer():
    bkpmgmt.remove(
        hist(),
        customer=None,
        vault=None,
    )


def test_history_show():
    bkpmgmt.history_show(hist())
