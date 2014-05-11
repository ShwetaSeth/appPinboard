

from flask.ext.couchdb import *

class User(Document):
	doc_type = 'User'
	firstName = TextField()
	lastName = TextField()
	emailId = TextField()
	password = TextField()
	userId = IntegerField()


class Board(Document):
	doc_type = 'Board'
	userId = IntegerField()
	boardName = TextField()
	boardDesc = TextField()
	category = TextField()
	isPrivate = BooleanField()



class Pin(Document):
	doc_type = 'Pin'
	userId = IntegerField()	
	pinId = IntegerField()
	boardName = TextField()
	pinName = TextField()
	image = TextField()
	description = TextField()


class Session(Document):
	doc_type = 'Session'	 
	userId = IntegerField()	
	

class Comment(Document):
	doc_type = 'Comment'
	userId = IntegerField()	
	pinId = IntegerField()
	boardName = TextField()
	commentId = IntegerField()	
	commentDesc = TextField()








