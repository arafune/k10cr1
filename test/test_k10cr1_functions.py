#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for functions in k10cr1.py (dth, btd)"""

from random import randint

from K10CR1.k10cr1 import dth
from K10CR1.k10cr1 import btd
from K10CR1.k10cr1 import digit_to_hex


class Test_equality_dth_digit_to_hex:
    def test_bit1(self) -> None:
        for i in range(-(2 ** (8 * 1)) / 2, 2 ** (8 * 1) / 2 - 1):
            print(i)
            assert dth(i, 1) == decimal_to_hex(i, 1)

    def test_bit2(self) -> None:
        for _ in range(1000):
            x: int = randint(-(2 ** (8 * 2)) / 2, 2 ** (8 * 2) / 2 - 1)
            assert dth(x, 2) == decimal_to_hex(x, 2)

    def test_bit4(self) -> None:
        for _ in range(100000):
            x: int = randint(-(2 ** (8 * 4)) / 2, 2 ** (8 * 4) / 2 - 1)
            assert dth(x, 4) == decimal_to_hex(x, 4)


class Test_dth:
    def test(self):
        assert dth(-128, 1) == "80"
        assert dth(128, 1) == "80"
        assert dth(256, 1) == "010"  # Should raise error!!
        assert dth(256, 2) == "0001"
        assert dth(4, 1) == "04"
        assert dth(4, 4) == "04000000"
        assert dth(4, 6) == "040000000000"
        assert dth(-4, 4) == "fcffffff"
        assert dth(-4, 1) == "fc"
        assert dth(14, 4) == "0e000000"
        assert dth(14, 1) == "0e"
        assert dth(-14, 1) == "f2"
        assert dth(-14, 4) == "f2ffffff"
        assert dth(254, 4) == "fe000000"
        assert dth(255, 1) == "ff"
        assert dth(-255, 2) == "01ff"
        assert dth(256, 4) == "00010000"
        assert dth(-256, 4) == "00ffffff"
        assert dth(-255, 4) == "01ffffff"
        assert dth(-596, 4) == "acfdffff"
        assert dth(-100596, 4) == "0c77feff"
        assert dth(64940, 4) == "acfd0000"
        assert dth(127, 1) == "7f"


class Test_btd:
    def test_all(self):
        assert btd(bytes.fromhex("acfdffff")) == -596
        assert btd(bytes.fromhex("0c77feff")) == -100596
        assert btd(bytes.fromhex("ff")) == -1
        assert btd(bytes.fromhex("fc")) == -4
        assert btd(bytes.fromhex("ef")) == -17
        assert btd(bytes.fromhex("ee")) == -18
        assert btd(bytes.fromhex("ed")) == -19
        assert btd(bytes.fromhex("f0")) == -16
        assert btd(bytes.fromhex("f1")) == -15
        # assert btd(bytes.fromhex("80")) == -128  ## Error !!
