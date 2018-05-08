#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from bkpmgmt import version


def test_version():
    assert type(version.__version__) == str
