#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Test for class history"""

import os

import pytest

from backupctl import history

BACKUPCTL_DB = os.path.join(
    os.sep,
    'tmp',
    'backupctl',
    'backupctl.db',
)


@pytest.fixture(autouse=True)
def hist():
    if not os.path.exists(os.path.dirname(BACKUPCTL_DB)):
        os.makedirs(os.path.dirname(BACKUPCTL_DB))
    hist_obj = history.History(BACKUPCTL_DB)
    return hist_obj


def test_add_customer():
    assert hist().add(
        customer='customer1',
        size='10G',
        command='test',
    )


def test_add_vault():
    assert hist().add(
        customer='customer1',
        vault='www.example.com',
        size='10G',
        command='test',
    )


def test_show_one():
    hist().add(
        customer='customer1',
        size='10G',
        command='test',
    )
    hist().add(
        customer='customer2',
        size='20G',
        command='test',
    )
    tdata = hist().show(
        count=1
    )
    assert type(tdata) == list
    assert len(tdata) == 1


def test_show_default():
    tdata = hist().show()
    assert type(tdata) == list
