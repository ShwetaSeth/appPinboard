#!flask/bin/python
import json as simplejson
from flask import Flask, g, request
from couchdb.design import ViewDefinition
import flask.ext.couchdb
import couchdb
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField
import datetime
from documents import User
from StringIO import StringIO


app = Flask(__name__)

get_passwords = ViewDefinition('login', 'password', 
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc.password);}')


get_userId = ViewDefinition('login', 'password', 
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc.userId);}')

get_Id = ViewDefinition('emailId', '_id', 
                                'function(doc) {if(doc.doc_type =="User")emit(doc.emailId, doc._id);}')



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

def checkPass(username,password):
	#docs = []
    	for row in get_passwords(g.couch)[username]:
        	#docs.append(row.value)
		if password == row.value:
			return True
		else:
			return False

def checkPass(emailId,password):
	docs = []
    	for row in get_passwords(g.couch)[emailId]:
        	docs.append(row.value)

		if password == row.value:
			return True
		else:
			return False


	

