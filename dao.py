#!flask/bin/python
import json as simplejson
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import flask.ext.couchdb
import couchdb
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField
import datetime
from documents import *
from StringIO import StringIO
from io import BytesIO
import pycurl


app = Flask(__name__)

get_passwords = ViewDefinition('login', 'password', 
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc);}')


get_userId = ViewDefinition('login', 'userId',
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc.userId);}')

#to get all boards for a user
get_boards = ViewDefinition('userId', 'board', 
                                'function(doc) {if(doc.doc_type =="Board")emit(doc.userId,doc);}')

#to get board by boardname for a user
#need to change the design model and view name cant keep same as above
get_board = ViewDefinition('get', 'board', 
                                'function(doc) {if(doc.doc_type =="Board")emit([doc.userId,doc.boardName],doc);}')
#to update a board
update_board = ViewDefinition('update', 'board', 
                                'function(doc) {if(doc.doc_type =="Board")emit([doc.userId,doc.boardName],doc);}')

get_pins = ViewDefinition('userId', 'pins', 
                                'function(doc) {if(doc.doc_type =="Pin")emit([doc.userId,doc.boardName],doc);}')



#to update a pin
get_pin = ViewDefinition('update', 'pin', 
                                'function(doc) {if(doc.doc_type =="Pin")emit([doc.userId,doc.boardName,doc.pinId],doc);}')


#get userId from session
get_session_userId = ViewDefinition('session', 'userId', 
                                'function(doc) {if(doc.doc_type =="Session")emit(null,doc.userId);}')


get_sessions = ViewDefinition('get', 'sessions', 
                                'function(doc) {if(doc.doc_type =="Session")emit(null,doc);}')

get_comments = ViewDefinition('userId', 'comments', 
                                'function(doc) {if(doc.doc_type =="Comment")emit([doc.userId,doc.boardName,doc.pinId],doc);}')

get_comment = ViewDefinition('userId', 'comments', 
                                'function(doc) {if(doc.doc_type =="Comment")emit([doc.userId,doc.boardName,doc.pinId,doc.commentId],doc);}')

#to update a comment
update_comment = ViewDefinition('update', 'comment', 
                                'function(doc) {if(doc.doc_type =="Comment")emit([doc.userId,doc.boardName,doc.pinId,commentId],doc);}')




def createSession(uid, bName,pid):

	session = Session(
		userId = uid,
		)
	session.store()
	return None	

def getSessionUserId():
	docs = []
	for row in get_session_userId(g.couch):
		docs.append(row.value)

	return docs[-1]





def register(fname,lname,email,passw):
	docs = []
    	for row in get_userId(g.couch):
		docs.append(row.value)

	if not docs:	
		uid = 0
	else:
		uid = docs[-1]
	
	user = User(
		firstName = fname,
		lastName = lname,
		emailId= email, 
		password = passw,
		userId = uid+1
		)
	user.store()
	return None


def checkPass(emailId,password):
	
    	for row in get_passwords(g.couch)[emailId]:
        	user = row.value


		if password == user['password']:
			createSession(user['userId'],None,0)
			return True
		else:
			return False


def createboard(uid, bName,bDesc,bcategory,bisPrivate):

	check = checkboardname(uid, bName)

	#if check is true board exists and should not be created
	if check is True:
		return 'Board already exists'

	else:
		board = Board(
			userId = uid,
			boardName = bName,
			boardDesc = bDesc,
			category = bcategory,
			isPrivate = False
		     )
	
		board.store()
	
		return getBoardByBoardname(uid, bName)


def checkboardname(uid, bName):
	board = []
	for row in get_board(g.couch)[int(uid),bName]:
		board.append(row.value)

	if board:
		return True
	else:
		return False
	
def createpin(uid,bName,pName,pimage,pdesc):
	docs = []
    	for row in get_pins(g.couch)[int(uid),bName]:
		docs.append(row.value)
		val = row.value

	if not docs:	
		pid = 0
	else:
		pid = val['pinId']

	pin = Pin(
			userId = uid,
			boardName = bName,
			pinName = pName,
			image = pimage,
			description = pdesc,	
			pinId = int(pid)+1
		     )
	
	pin.store()
	newpid = int(pid)+1 
	return getpin(uid,bName,newpid)



def getpins(userId,bName):
	pins = []
    	for row in get_pins(g.couch)[int(userId),bName]:
		pins.append(row.value)
		
	return pins



def getpin(uid,bName,pid):
	pin = []	
	for row in get_pin(g.couch)[int(uid),bName,int(pid)]:
		createSession(int(uid),bName,int(pid))
		pin.append(row.value)


	return pin[-1]
	


def updatepin(uid,bName,pName,pimage,pdesc,pid):
		
	for row in get_pin(g.couch)[int(uid),bName,int(pid)]:
		pin = row.value
	
	print 'pin is',pin['pinName']	
	
	if(pName is None):
   		pName = pin['pinName']
		
	if(pimage is None):
   		pimage = pin['image']
		
	if(pdesc is None):
   		pdesc = pin['description']



	newpin = Pin(
			userId = uid,
			boardName = bName,
			pinName = pName,
			image = pimage,
			description = pdesc,	
			pinId = pid
		     )
	newpin.store()
	
	for row in get_pin(g.couch)[int(uid),bName,int(pid)]:
		pin = row.value
	
    	
	return pin


def deletepin(uid,bName,pid):

	for row in get_pin(g.couch)[int(uid),bName,int(pid)]:
                # to delete all the revisions of a documents which might have gotten created during update
		pin = row.value
     		print 'http://localhost:5984/pinboard/',pin['_id'] ,'?_rev=',pin['_rev']
		
		c = pycurl.Curl()
		c.setopt(c.URL, 'http://localhost:5984/pinboard/'+pin['_id'] +'?rev='+pin['_rev'])
		#c.setopt(c.DELETEFIELDS, 'pid='+pid+'& userId='+uid+'& boardName='+bName)
		#c.setopt(c.POSTFIELDS, 'pinId=1')
		c.setopt(c.CUSTOMREQUEST,'DELETE')
		c.setopt(c.VERBOSE, True)
		c.perform()

	return None

	
def updateboard(uid,bDesc,bName,categ):
		
	for row in update_board(g.couch)[int(uid),bName]:
		board = row.value
	
	#print 'board is', board['boardName']	
	
 	
	if(bDesc is None):
   		bDesc = board['boardDesc']
		
	if(bName is None):
   		bName = board['boardName']
		
	if(categ is None):
   		categ = board['category']

	newboard = Board(
			userId = uid,
			boardName = bName,
			boardDesc = bDesc,	
			category = categ
		     )
	newboard.store()
	
	for row in update_board(g.couch)[int(uid),bName]:
		board = row.value
	
    	
	return board


def getBoardsForUser(userId):
	#return get_boards(g.couch)[userId]
	boards = []
	
    	for row in get_boards(g.couch)[int(userId)]:
		boards.append(row.value)

	#print 'BOARDS' ,boards
	#return simplejson.dumps(boards)

	
	return boards

def getBoardByBoardname(userId, bname):
	board = []
	print userId,bname
	for row in get_board(g.couch)[int(userId),bname]:
		createSession(int(userId),bname,0)
		board.append(row.value)


	return board


def createcomment(uid,bName,pId,cDesc):
	comments = []
    	for row in get_comments(g.couch)[int(uid),bName]:
		comments.append(row.value)
		val = row.value

	if not comments:	
		cid = 0
	else:
		cid = val['commentId']

	comment = Comment(
			userId = uid,
			boardName = bName,
			pinId = pId,
			commentId = cid+1,
			commentDesc = cDesc
		     )
	
	comment.store()
	return None

def updatecomment(uid,bName,pid,cid,cDesc):
		
	for row in update_comment(g.couch)[int(uid),bName,int(pid),int(cid)]:
		comment = row.value
	
	print 'comment is',comment['commentDesc']	
	
	if(cDesc is None):
   		cDesc = comment['commentDesc']
	

	newcomment = Comment(
			userId = uid,
			boardName = bName,
			pinId = pid,
			commentId = cid,
			commentDesc = cDesc
		     )
	newcomment.store()
	
	for row in update_comment(g.couch)[int(uid),bName,int(pid),int(cid)]:
		comment = row.value
	
    	
	return comment

def deletepin(uid,bName,pid):

	for row in _pin(g.couch)[int(uid),bName,int(pid)]:
                # to delete all the revisions of a documents which might have gotten created during update
		pin = row.value
     		print 'http://localhost:5984/pinboard/',pin['_id'] ,'?_rev=',pin['_rev']
		
		c = pycurl.Curl()
		c.setopt(c.URL, 'http://localhost:5984/pinboard/'+pin['_id'] +'?rev='+pin['_rev'])
		#c.setopt(c.DELETEFIELDS, 'pid='+pid+'& userId='+uid+'& boardName='+bName)
		#c.setopt(c.POSTFIELDS, 'pinId=1')
		c.setopt(c.CUSTOMREQUEST,'DELETE')
		c.setopt(c.VERBOSE, True)
		c.perform()

	return None

def deleteBoardForuser(userId, bname):
	 # to delete all the revisions of a documents which might have gotten created during update
	for row in get_board(g.couch)[int(userId),bname]:   
		board = row.value
		c = pycurl.Curl()
		c.setopt(c.URL, 'http://localhost:5984/pinboard/'+board['_id'] +'?rev='+board['_rev'])
		#c.setopt(c.DELETEFIELDS, 'pid='+pid+'& userId='+uid+'& boardName='+bName)
		#c.setopt(c.POSTFIELDS, 'pinId=1')
		c.setopt(c.CUSTOMREQUEST,'DELETE')
		c.setopt(c.VERBOSE, True)
		c.perform()
		return None


def clearSession(userId):
	for row in get_sessions(g.couch):   
		user = row.value
		c = pycurl.Curl()
		c.setopt(c.URL, 'http://localhost:5984/pinboard/'+user['_id'] +'?rev='+user['_rev'])
		#c.setopt(c.DELETEFIELDS, 'pid='+pid+'& userId='+uid+'& boardName='+bName)
		#c.setopt(c.POSTFIELDS, 'pinId=1')
		c.setopt(c.CUSTOMREQUEST,'DELETE')
		c.setopt(c.VERBOSE, True)
		c.perform()
		return None



