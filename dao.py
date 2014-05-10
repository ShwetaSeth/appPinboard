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
                                'function(doc) {if(doc.doc_type =="User")emit(doc.username, doc.password);}')


def register(fname,lname,uname,passw):
	user = User(
		firstname = fname,
		lastname = lname,
		username= uname, 
		password = passw
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

#def getuser(username)
	

