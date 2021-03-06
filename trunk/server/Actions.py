#!/usr/bin/env python
"""
$Id: Actions.py,v 1.2 2005/04/19 04:10:53 rohan Exp $

Generic acton structure.
"""

import threading, time

class Action:
	"""
	Base Action object.
	"""
	def __init__(self, server, params):
		self.params = params
		self.server = server
	
	def start(self):
		print "BASE ACTION ITEM USED. Please overload this."
		return False
		
	def think(self):
		print "BASE ACTION ITEM USED. Please overload this."
		
	def stop(self):
		print "BASE ACTION ITEM USED. Please overload this."

class ActionHandler(threading.Thread):
	def __init__(self, purpose, server, actionMap, noKeys = 0):
		threading.Thread.__init__(self)
		self.server = server
		self.purpose = purpose
		self.noKeys = noKeys
		if not actionMap:
			print "ERROR: No action map passed in to %s handler." % self.purpose
		self.actionMap = actionMap
		if self.noKeys:
			self.events = []
		else:
			self.events = {}

	def run(self):
		print "Running %s handler." % self.purpose
		self.mainLoop()
	
	def mainLoop(self):
		self.startTime = time.time()
		print "Started %s handler at %s" % (self.purpose, self.startTime)
		alt = 1
		lastTick = time.time()
		while self.server.running:
			now = time.time()
			if now - lastTick > 1:
				lastTick += 1
				self.think(now - lastTick)
		print "%s handler finished." % self.purpose
	
	def actions(self):
		"""
		Return all actions we support.
		"""
		return self.actionMap.keys()

	def addAction(self, key, action, params):
		"""
		Add a new action.
		"""
		if self.noKeys:
			pass
		else:
			if not key not in self.actionMap.keys():
				print "Unknown action '%s' attempted." % key
			self.realStopAction(key)
			frequency, actionFn = self.actionMap[action]
			self.events[key] = [actionFn(self.server, params), frequency, 1]
			if not self.events[key][0].start():
				print "Failed to start action."
				del self.events[key]
	
	def stopAction(self, key):
		if self.noKeys:
			pass
		else:
			return self.realStopAction(key)
	
	def realStopAction(self, key):
		if self.events.has_key(key):
			self.events[key][0].stop()
			del self.events[key]
			return True
		return False
	
	def think(self, offset):
		if self.noKeys:
			pass
		else:
			# Keyed on userID, only one action per key.
			toChange = {}
			for key, (function, frequency, tick) in self.events.items():
				# Events can happen more than one pass. If frequency is set to
				# '2', it will happen every second time around the loop.
				if tick >= frequency:
					function.think()
					toChange[key] = 1
				else:
					toChange[key] = tick + 1
			for eventKey, value in toChange.items():
				self.events[eventKey][2] = value

	def __del__(self):
		print "%s handler destroyed." % self.purpose
