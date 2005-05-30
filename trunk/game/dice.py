#!/usr/bin/env python
"""
$Id$

Support funtions for dice-rolling, non engine-specific.
"""

from random import Random

rnd = Random()


def d6(dice = 1):
	return rnd.randint(dice, dice * 6)

def d10(dice = 1):
	return rnd.randint(dice, dice * 10)

def d100(dice = 1):
	return rnd.randint(dice, dice * 100)
