#!flask/bin/python
from flask import Flask, jsonify, g, request,session, redirect, url_for, escape ,Response
from flask.ext.login import LoginManager
import datetime
#pip install pycurl
import pycurl
#apt-get install python-tk
#import urllib
from documents import *
import flask.ext.couchdb
from dao import *
import couchdb
from couchdb import Server
import json as simplejson
from couchdb.design import ViewDefinition



app = Flask(__name__)


#login_manager = LoginManager(app)

login_manager = LoginManager()
login_manager.init_app(app)


from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

#curl -i -H "Content-Type: application/json" -X POST -d '{"firstName":"Bharat","lastName":"Mehndiratta","emailId":"bharat@gmail.com","password":"bharat16"}' http://localhost:5000/signup
@app.route('/signup', methods = ['POST'])
def signup():
	if not request.json or not 'emailId' in request.json:
        	abort(400)
	register(request.json['firstName'],request.json['lastName'],request.json['emailId'],request.json['password'])
	return jsonify( { 'Sign Up Message': 'Sign up Successfull' } )


@auth.verify_password
def verify_password(emailId, password):
	return checkPass(emailId,password)

@auth.error_handler
def unauthorized():
    return jsonify( { 'error': 'Unauthorized access' } ), 401

@app.route('/')
def index():
    if 'emailId' in session:
        return 'Logged in as %s' % escape(session['emailId'])
    return 'You are not logged in'

#curl -u bharat@gmail.com:bharat16-i http://localhost:5000/login
@app.route('/login', methods = ['GET','POST'])
@auth.login_required
def get_tasks():



   	flask.ext.login.confirm_login()
	#if request.method == 'POST':
        #session['emailId'] = emailId
   	return jsonify({
   	 "Links":[
        	{
            		"url": "/users/<userId>/boards/",
            		"method": "GET"
        	},
        	{
            		"url": "/users/<userid>/boards/",
            		"method": "POST"
        	}
	    ]
	}), 201




@app.route("/logout")
@auth.login_required
def logout():

   	flask.ext.login.logout_user()
	#session.pop('emailId', None)
    	return jsonify( { 'Log out Message': 'Log out Successfull' } )

	


	
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


#curl -i -H "Content-Type: application/json" -X POST -d '{"boardName":"Recipes","boardDesc":"Indian food recipes","category":"Food","isPrivate":"false"}' http://localhost:5000/users/1/boards

@app.route('/users/<userId>/boards', methods = ['POST'])
def createBoard(userId):
	
	boardName = request.json['boardName']
	boardDesc = request.json['boardDesc']
	category = request.json['category']
	isPrivate = request.json['isPrivate']

	createboard(userId,boardName,boardDesc,category,isPrivate)
	
	return jsonify( { 'Board Creation Message': 'Board Creation Successful' } )



#curl -i http://localhost:5000/users/1/boards


#curl -i -H "Content-Type: application/json" -X POST -d '{"pinName":"Rasberry Salad","image":"image of rasberry salad","description":"yummy and healthy salad"}' http://localhost:5000/users/1/boards/Recipes/pins
@app.route('/users/<userId>/boards/<boardName>/pins', methods = ['POST'])
def createPin(userId,boardName):	
	pinName = request.json['pinName']
	image = request.json['image']
	description = request.json['description']

	createpin(userId,boardName,pinName,image,description)
	
	return jsonify( { 'Pin Creation Message': 'Pin Creation Successful' } )

#curl -i -H "Content-Type: application/json" -X POST -d '{"commentDesc":"wonderful idea!"}' http://localhost:5000/users/1/boards/123/pins/1/comment
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comment', methods = ['POST'])
def createComment(userId,boardName,pinId):	
	commentDesc = request.json['commentDesc']

	createcomment(userId,boardName,pinId,commentDesc)
	
	return jsonify( { 'Comment Creation Message': 'Comment Creation Successful' } )



#curl -X GET http://localhost:5000/users/1/boards
@app.route('/users/<userId>/boards', methods = ['GET'])
def getBoards(userId):
	
	boards = getBoardsForUser(userId)
	#print boards
	#resp = jsonify(boards)
	#resp.status_code = 200
	#return boards
	
	return jsonify( { 'Boards': boards } )


#curl -X GET http://localhost:5000/users/1/boards/Recipes/pins
@app.route('/users/<userId>/boards/<boardName>/pins', methods = ['GET'])
def getPins(userId,boardName):
	pins = getpins(userId,boardName)
	return jsonify( { 'Pins': pins } )

#curl -X GET http://localhost:5000/users/2/boards/Recipes
@app.route('/users/<userId>/boards/<boardName>', methods = ['GET'])
def getBoard(userId,boardName):
	board = getBoardByBoardname(userId,boardName)
	return jsonify( { 'Board': board } )


#curl -i -H "Content-Type: application/json" -X PUT -d '{"pinName":"Salad Love"}' http://localhost:5000/users/1/boards/Recipes/pins/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>', methods = ['PUT'])
def updatePin(userId,boardName,pinId):
	
   	if 'pinName' in request.json and type(request.json['pinName']) is not unicode:
        	abort(400)

    	if 'image' in request.json and type(request.json['image']) is not unicode:
        	abort(400)

   	if 'description' in request.json and type(request.json['description']) is not unicode:
        	abort(400)

	if 'pinName' in request.json:
		pinName = request.json['pinName']
	else:
		pinName = None

	if 'image' in request.json:
		image = request.json['image']
	else:
		image = None

	if'description' in request.json:
		description = request.json['description']
	else:
		description = None

	pin = updatepin(userId,boardName,pinName,image,description,pinId)

	return jsonify( { 'Pin': pin } )


#curl -i -H "Content-Type: application/json" -X PUT -d '{"boardName":"Recipes_changed","category":"caegory_changed", "boardDesc":"description_changed"}' http://localhost:5000/users/1/boards/123
@app.route('/users/<userId>/boards/<boardName>', methods = ['PUT'])
def updateBoard(userId,boardName):
	
   	if 'boardName' in request.json and type(request.json['boardName']) is not unicode:
        	abort(400)

    	if 'boardDesc' in request.json and type(request.json['boardDesc']) is not unicode:
        	abort(400)

   	if 'category' in request.json and type(request.json['category']) is not unicode:
        	abort(400)

	if 'boardName' in request.json:
		boardName = request.json['boardName']
	else:
		boardName = None

	if 'boardDesc' in request.json:
		boardDesc = request.json['boardDesc']
	else:
		boardDesc = None

	if'category' in request.json:
		category = request.json['category']
	else:
		category = None
	
	print userId , boardName,boardDesc,category
	board = updateboard(userId,boardName,boardDesc,category)

	return jsonify( { 'New Board': board } )

#curl -X GET http://localhost:5000/users/2/boards/Recipes
@app.route('/users/<userId>/boards/<boardName>/delete', methods = ['DELETE'])
def deleteBoard(userId,boardName):
	deleteBoardForuser(userId,boardName)
	return jsonify( { 'Board': 'Board Deleted' } )


#curl -X DELETE http://localhost:5000/users/1/boards/Recipes/pins/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>', methods = ['DELETE'])
def deletePin(userId,boardName,pinId):	
	deletepin(userId,boardName,pinId)
	return jsonify( { 'Delete': 'Deleted' } )



if __name__ == '__main__':
	app.config.update(
        	DEBUG = True,
        	COUCHDB_SERVER = 'http://localhost:5984/',
        	COUCHDB_DATABASE = 'pinboard'
    	)
   	manager = flask.ext.couchdb.CouchDBManager()
    	manager.setup(app)
    	manager.add_viewdef(get_passwords)  # Install the view
	manager.add_viewdef(get_userId)    
	manager.add_viewdef(get_boards)
	manager.add_viewdef(get_pins)
	manager.add_viewdef(get_board)
	manager.add_viewdef(update_pin)

	manager.add_viewdef(update_board)
	manager.add_viewdef(get_comments)

	manager.add_viewdef(delete_pin)
	


	  	
	manager.sync(app)

	app.run(host='0.0.0.0', port=5000)

	DB_URL = 'http://localhost:5984/pinboard'
    	#app.run(debug = True)
