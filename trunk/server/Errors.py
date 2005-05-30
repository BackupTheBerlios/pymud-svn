#!/usr/bin/env python
"""
$Id: Errors.py,v 1.2 2005/05/06 01:59:09 rohan Exp $

Error classes.
"""

class GameError(Exception):
	def __init__(self, error = "Unknown Error"):
		self.details = error
		Exception.__init__(self)
	
	def __str__(self):
		return self.details
