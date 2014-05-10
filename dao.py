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


app = Flask(__name__)

get_passwords = ViewDefinition('login', 'password', 
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc.password);}')


get_userId = ViewDefinition('login', 'userId',
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc.userId);}')


get_boards = ViewDefinition('userId', 'boardname', 
                                'function(doc) {if(doc.doc_type =="Board")emit(doc.userId,doc);}')

get_pins = ViewDefinition('userId', 'pins', 
                                'function(doc) {if(doc.doc_type =="Pin")emit([doc.userId,doc.boardName],doc);}')


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
	docs = []
    	for row in get_passwords(g.couch)[emailId]:
        	docs.append(row.value)


		if password == row.value:
			return True
		else:
			return False

def createboard(uid, bName,bDesc,bcategory,bisPrivate):
	board = Board(
			userId = uid,
			boardName = bName,
			boardDesc = bDesc,
			category = bcategory,
			isPrivate = bcategory
		     )
	
	board.store()
	return None


def createpin(uid,bName,pName,pimage,pdesc):
	pin = Pin(
			userId = uid,
			boardName = bName,
			pinName = pName,
			image = pimage,
			description = pdesc
		     )
	
	pin.store()
	return None

def getpins(userId,bName):
	pins = []
    	for row in get_pins(g.couch)[int(userId),bName]:
		pins.append(row.value)
		
	return pins

	
	

