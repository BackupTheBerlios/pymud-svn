#!/usr/bin/env python
"""
$Id$

Data handlers and objects - IE, all hard-coded data and database access
utility functions.
"""
import sha
from types import ListType, TupleType
from string import lower, strip
from utils import pgDB
import server.Queries as Q
import server.DBConstants as DC

# Different userlevels

Admin = 5
Player = 0

def getUsersInRoom(cursor, roomid):
	query = Q.GetUsersInRoom % {DC.Location: roomid}
	return pgDB.fetch(cursor, query)

def getThreadsInRoom(cursor, roomid):
	query = Q.GetThreadsInRoom % {DC.Location: roomid}
	return pgDB.fetchList(cursor, query)

def updateLocation(cursor, userid, location):
	queryDict = {
		DC.UserID: userid,
		DC.Location: location,
	}
	query = Q.UpdateLocation % queryDict
	pgDB.execute(cursor, query)

def getLocation(cursor, userid):
	queryDict = {
		DC.UserID: userid,
	}
	query = Q.GetLocation % queryDict
	return pgDB.fetchOneValue(cursor, query)

def clearLoggedInUsers(cursor):
	query = Q.ClearLoggedInUsers
	pgDB.execute(cursor, query)

def getThreadID(cursor, userid):
	query = Q.GetThreadID % {DC.UserID: userid}
	return pgDB.fetchOneValue(cursor, query)

def setThreadID(cursor, userid, threadid):
	query = Q.SetThreadID % {DC.UserID: userid, DC.CurrentThreadID: threadid}
	pgDB.execute(cursor, query)

def getThreads(cursor, useridList):
	print useridList
	users = "('" + "','".join(useridList) + "')"
	query = Q.GetThreads % users
	return pgDB.fetch(cursor, query)

def createUser(cursor, nickname, charname, password, userlevel = Player):
	password = sha.new(password).hexdigest()
	queryDict = {
		DC.UserID: userid,
		DC.UserLevel: userlevel,
		DC.NickName: nickname,
		DC.FullName: charname,
		DC.Password: password,
	}
	query = Q.CreateUser % queryDict
	pgDB.execute(query)

def getArea(cursor, roomid):
	query = Q.GetAreaID % {DC.RoomID: roomid}
	return pgDB.fetchOneValue(cursor, query)

def getPasswordHash(cursor, userid):
	query = Q.GetPassword % {DC.UserID: userid}
	return pgDB.fetchOneValue(cursor, query)

def getUserData(cursor, userid, field = None):
	"""
	Return either one, some, or all of the fields in the UserData
	table for the given userid.
	"""
	if not field:
		query = Q.GetAllUserData % {DC.UserID: userid}
		res = pgDB.fetchDict(cursor, query)
		return res[0]
	else:
		if type(field) in (ListType, TupleType):
			field = ','.join(field)
			query = Q.GetUserData % (field, userid)
			return pgDB.fetchOne(cursor, query)
		else:
			query = Q.GetUserData % (field, userid)
			return pgDB.fetchOneValue(cursor, query)

def getExits(cursor, roomid):
	query = Q.GetExits % {DC.RoomID: roomid}
	res = pgDB.fetchOne(cursor, query)
	try:
		name1, room1, name2, room2, \
		name3, room3, name4, room4 = res
	except TypeError:
		# Area does not exist.
		print "ERROR! User attempted to go to room %s, which, "\
		"seemingly, does not exist." % roomid
	exits = {}
	if room1:
		area = getArea(cursor, room1)
		exits[lower(name1)] = room1, area
	if room2:
		area = getArea(cursor, room2)
		exits[lower(name2)] = room2, area
	if room3:
		area = getArea(cursor, room3)
		exits[lower(name3)] = room3, area
	if room4:
		area = getArea(cursor, room4)
		exits[lower(name4)] = room4, area
	return exits

# Area/Room information
def getRoomDescription(cursor, roomid):
	"""
	Gets the room decription from the database.
	"""
	query = Q.GetRoomDescription % {DC.RoomID: roomid}
	res = pgDB.fetchOneValue(cursor, query)
	if not res:
		#FIXME We need an /unstick command that resets peoples location.
		res = "You seem to be stuck. Please contact an"\
		" administrator and tell them that you've gotten somewhere"\
		" you shouldn't be able to get to."
	return res

def getRoomItems(cursor, roomID):
	"""
	Gets items in the room from the database.
	"""
	query = Q.GetItemsInRoom % {DC.RoomID: roomID}
	res = pgDB.fetchList(cursor, query)
	return res
			
def getItemDescription(cursor, roomid, cmd):
	query = Q.GetItemDescription % {DC.RoomID: roomid}
	res = pgDB.fetch(cursor, query)
	cmd = cmd[1]
	desc = "You look around but you can't see a %s.\r\n" %cmd
	for description, keywords in res:
		keywords = keywords.split(",")
		if cmd in keywords:
			desc = description + "\r\n"
	return desc

def getItemForUser(cursor, cmdList, roomID, username):
	"""
	Gives a user the item they tried to pickup if possible.
	"""
	query = Q.GetItemsForUser % {DC.RoomID: roomID}
	res = pgDB.fetch(cursor, query)
	print "res = %s" %res
	cmd = cmdList[1]
	print "cmd = %s" %cmd
	desc = "You screw your eyes shut and wish really hard for a %s\r\n" %cmd
	for itemID, keywords, itemCount in res:
		keywords = keywords.split(",")
		print "keywords %s" %keywords
		if cmd in keywords:
			print "cmd in keywords"
			print "itemCount %s"  %itemCount
			if int(itemCount) > 0:
				print "hello" 
				# FIXME: Do all these queries in one transaction.
				# Get The users existing inventory.
				InventoryQ = Q.GetUserInventory % {"UserID":username}
				inventory = pgDB.fetchOne(cursor, InventoryQ)

				# Remove one of the item from the room it was in.
				itemCount = int(itemCount) - 1
				UpdateCount = Q.UpdateItemCount % {"ItemID":itemID,
												"ItemCount":itemCount,}
				pgDB.executeOne(cursor, UpdateCount)

				# Place one of the item into the users inventory.
				newInventory = []
				existing = ""
				if inventory[0]:
					print "inventory %s" %repr(inventory)
					inventory = inventory.split(",")
					for item, count in inventory[0].split(":"):
						if itemID == item:
							count = int(count) + 1
							existing = "1"
							newInventory.append("%s:%s" %(itemID, str(count)))
						else:
							newInventory.append("%s:%s" %(itemID, count))
							
				if not existing:
					newInventory.append("%s:1" %itemID)
				
				newInventory = ",".join(newInventory)
				
				UpdateInvQ = Q.UpdateUserInventory % {"UserID":username,
													"Inventory":newInventory,}
				pgDB.executeOne(cursor, UpdateInvQ)
			else:
				desc = "You pickup a %s\r\n" %cmd
	return desc
			
# Game states
GameStates = {
	"PreLogin": "PreLogin",
	"Password": "Password",
	"InGame": "InGame",
}

# Location Descriptions
Locations = {
	"Welcome" : "`%Login:",
	"Password" : "`%Password:",
	"InGame" : "You are in a big room.\r\n",
}

def motd():
	# Print the message of the day. Or rather, return it.
	message = """Welcome to The World.
Please enjoy your stay, and try not to leave a mess.

"""
	return message
