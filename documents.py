

from flask.ext.couchdb import *

class User(Document):
	doc_type = 'User'
	firstname = TextField()
	lastname = TextField()
	username = TextField()
	password = TextField()



