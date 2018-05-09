#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Test for class history"""

import pytest

from backupctl import history


@pytest.fixture(autouse=True)
def hist():
    hist_obj = history.History('/tmp/backupctl.db')
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
