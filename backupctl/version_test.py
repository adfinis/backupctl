#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from backupctl import version


def test_version():
    assert type(version.__version__) == str
