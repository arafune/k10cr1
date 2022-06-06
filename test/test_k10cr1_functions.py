#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for functions in k10cr1.py (dth, btd)"""

from K10CR1.k10cr1 import dth
from K10CR1.k10cr1 import btd


class Test_dth:
    assert dth(4, 1) == '04'
    assert dth(4, 4) == '04000000'
    assert dth(4, 6) == '040000000000'
    assert dth(-4, 4) == 'fcffffff'
    assert dth(-4, 1) == 'fc'
    assert dth(14, 4) == '0e000000'
    assert dth(14, 1) == '0e'
    assert dth(254, 4) == 'fe000000'
    assert dth(255, 4) == 'ff000000'
    assert dth(256, 4) == '00010000'
    assert dth(-256, 4) == '00ffffff'
    assert dth(-255, 4) == '01ffffff'

class Test_btd:
    pass
