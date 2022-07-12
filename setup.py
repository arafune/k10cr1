#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="K10CR1",
    version="1.0",
    description="Thorlabs K10CR1 rotation stage driver",
    url="https://github.com/QuantumQuadrate/k10cr1",
    packages=find_packages(),
    install_requires=["pyserial"],
    license="MIT",
)
