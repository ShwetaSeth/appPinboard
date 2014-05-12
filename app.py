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
	return jsonify( { 
	"Links":[
        	{
            		"url": "/users/login",
            		"method": "POST"
        	}
	    ]
	}), 201


@auth.verify_password
def verify_password(emailId, password):
	#if request.method == 'POST':
        session['emailId'] =  emailId
	email = emailId
	print 'session is', session['emailId']
	return checkPass(emailId,password)

@auth.error_handler
def unauthorized():
    return jsonify( { 'error': 'Unauthorized access' } ), 401

@app.route('/')
def index():
	#print 'session is', session['emailId']
	print 'Email is', email
    	if 'emailId' in session:
      	  return 'Logged in as %s' % escape(session['emailId'])
    	return 'You are not logged in'

#curl -u bharat@gmail.com:bharat16 -i http://localhost:5000/login
@app.route('/login', methods = ['GET','POST'])
@auth.login_required
def get_tasks():

	session_userId = getSessionUserId()


   	flask.ext.login.confirm_login()
	#if request.method == 'POST':
        #session['emailId'] = emailId
   	return jsonify({
   	 "Links":[
        	{
            		"url": "/users/"+str(session_userId)+"/boards/",
            		"method": "GET"
        	},
        	{
            		"url": "/users/"+str(session_userId)+"/boards/",
            		"method": "POST"
        	}
	    ]
	}), 201



@app.route("/<userId>/logout", methods = ['GET'])
def logout(userId):

	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )
	
	
	clearSession(userId)

   	flask.ext.login.logout_user()
    	return jsonify( { 'Log out Message': 'Log out Successfull' } ), 201

	


	


#CREATE BOARD
#curl -i -H "Content-Type: application/json" -X POST -d '{"boardName":"Recipes","boardDesc":"Indian food recipes","category":"Food","isPrivate":"false"}' http://localhost:5000/users/1/boards

@app.route('/users/<userId>/boards', methods = ['POST'])
def createBoard(userId):
		
		
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	else:
		boardName = request.json['boardName']
		boardDesc = request.json['boardDesc']
		category = request.json['category']
		isPrivate = request.json['isPrivate']

		board = createboard(userId,boardName,boardDesc,category,isPrivate)
	
		return jsonify( { 'Board': board} ),201


#curl -i -H "Content-Type: application/json" -X POST -d '{"pinName":"Rasberry Salad","image":"image of rasberry salad","description":"yummy and healthy salad"}' http://localhost:5000/users/1/boards/Recipes/pins
@app.route('/users/<userId>/boards/<boardName>/pins', methods = ['POST'])
def createPin(userId,boardName):
	session_userId = getSessionUserId()


	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	
		
	pinName = request.json['pinName']
	image = request.json['image']
	description = request.json['description']

	pin = createpin(userId,boardName,pinName,image,description)
	
	return jsonify( { 'Pin': pin } ),201

#curl -i -H "Content-Type: application/json" -X POST -d '{"commentDesc":"wonderful idea!"}' http://localhost:5000/users/1/boards/123/pins/1/comment
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comment', methods = ['POST'])
def createComment(userId,boardName,pinId):	
	commentDesc = request.json['commentDesc']

	comment = createcomment(userId,boardName,pinId,commentDesc)
	
	return jsonify( { 'Comment Creation Message': comment  } ),201



#curl -X GET http://localhost:5000/users/1/boards
@app.route('/users/<userId>/boards', methods = ['GET'])
def getBoards(userId):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	
	boards = getBoardsForUser(userId)
	
	#print boards
	#resp = jsonify(boards)
	#resp.status_code = 200
	#return boards

	#return jsonify( { 'Boards': boards } ),201
	
	return  jsonify( { 
		"Boards and Link":[
        	{
            		"Boards": boards
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/<BoardName>",
            		"method": "GET"
        	},

		{
            		"url": "/users/"+str(session_userId)+"/boards/<BoardName>",
            		"method": "PUT"
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/<BoardName>",
            		"method": "DELETE"
        	}
		
	    ]
	}), 201


#curl -X GET http://localhost:5000/users/1/boards/Recipes/pins
@app.route('/users/<userId>/boards/<boardName>/pins', methods = ['GET'])
def getPins(userId,boardName):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	
	pins = getpins(userId,boardName)

	return  jsonify( { 
		"Pins and Links":[
        	{
            		"Pins": pins
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins/<pinId>",
            		"method": "GET"
        	},

		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins/<pinId>",
            		"method": "PUT"
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins/<pinId>",
            		"method": "DELETE"
        	}
		
	    ]
	}), 201

#curl -X GET http://localhost:5000/users/1/boards/Recipes
@app.route('/users/<userId>/boards/<boardName>', methods = ['GET'])
def getBoard(userId,boardName):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	board = getBoardByBoardname(userId,boardName)
	# on a board you can create a pin or get pins for further operations
	return  jsonify( { 
		"Status":[
        	{
            		"Board": board
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins",
            		"method": "POST"
        	},

		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins",
            		"method": "GET"
        	}
	
	    ]
	}), 201



#GET PIN FOR A PIN ID
#curl -X GET http://localhost:5000/users/1/boards/Recipes/pins/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>', methods = ['GET'])
def getPin(userId,boardName,pinId):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	pin = getpin(userId,boardName,pinId)

	return  jsonify( { 
		"Status":[
        	{
            		"Pin": pin
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins"+pinId+"/comments",
            		"method": "POST"
        	},

		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins"+pinId+"/comments",
            		"method": "GET"
        	}
	
	    ]
	}), 201

#GET COMMENTS for a PIN ID
#curl -X GET http://localhost:5000/users/1/boards/Recipes/pins/1/comments
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comments', methods = ['GET'])
def getComments(userId,boardName,pinId):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	
	comments = getcomments(userId,boardName,pinId)
	return  jsonify( { 
		"Status":[
        	{
            		"Comments": comments
        	},
		
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins"+pinId+"/comments/<commentId>",
            		"method": "GET"
        	},

		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins"+pinId+"/comments/<commentId>",
            		"method": "PUT"
        	},
		{
            		"url": "/users/"+str(session_userId)+"/boards/"+boardName+"/pins"+pinId+"/comment/<commentId>",
            		"method": "DELETE"
        	},
	
	    ]
	}), 201
		
		

#UPDATE PIN
#curl -i -H "Content-Type: application/json" -X PUT -d '{"pinName":"Salad Love"}' http://localhost:5000/users/1/boards/Recipes/pins/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>', methods = ['PUT'])
def updatePin(userId,boardName,pinId):
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	
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

#curl -X DELETE http://localhost:5000/users/1/boards/Recipes
@app.route('/users/<userId>/boards/<boardName>', methods = ['DELETE'])
def deleteBoard(userId,boardName):
	deleteBoardForuser(userId,boardName)
	
	board = getBoardByBoardname(userId,boardName)
	pins =  getpins(userId,boardName)
	# to show a board it is deleted
	return jsonify({
		"Deleted":[
        	{
            		"Board": board
        	},
		
		{
            		"Pins in board with comments": pins
            		
        	}
	
	    ]
		}), 201


#curl -X DELETE http://localhost:5000/users/1/boards/Recipes/pins/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>', methods = ['DELETE'])
def deletePin(userId,boardName,pinId):	
	session_userId = getSessionUserId()

	if int(userId) != session_userId:
		return jsonify( { 'Status': 'User not logged in'} )

	deletepin(userId,boardName,pinId)

	pins =  getpins(userId,boardName)
	comments = getcomments(userId,boardName,pinId)

	# to show a board it is deleted
	return  jsonify( { 
		"Deleted":[
        	{
            		"Pin": board
        	},
		
		{
            		"Comments in pin": comments
            		
        	}
	
	    ]
	}), 201

#curl -X GET http://localhost:5000/users/1/boards/Recipes/pins/1/comment/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comment/<commentId>', methods = ['GET'])
def getComment(userId,boardName,pinId,commentId):
	
	comment = getcomment(userId,boardName,pinId,commentId)
	

	# to show a comment it is deleted
	return  jsonify( { "Comment": comments }), 201



#curl -i -H "Content-Type: application/json" -X PUT -d '{"commentDesc":"New comment Description"}' http://localhost:5000/users/1/boards/Recipes/pins/1/comment/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comment/<commentId>', methods = ['PUT'])
def updateComment(userId,boardName,pinId,commentId):
	
   	if 'commentDesc' in request.json and type(request.json['commentDesc']) is not unicode:
        	abort(400)

	if 'commentDesc' in request.json:
		commentDesc = request.json['commentDesc']
	else:
		commentDesc = None

	comment = updatecomment(userId,boardName,pinId,commentId,commentDesc)

	return jsonify( { 'Updated Comment': comment } )



#curl -X DELETE http://localhost:5000/users/1/boards/Recipes/pins/1/comment/1
@app.route('/users/<userId>/boards/<boardName>/pins/<pinId>/comment/<commentId>', methods = ['DELETE'])
def deleteComment(userId,boardName,pinId,commentId):
	
	deletecomment(uid,bName,pid)
	comments = getcomments(userId,bName,pId)

	# to show a comment it is deleted
	return  jsonify( { 
		"Deleted":[
        	{
            		"Comment": comments
        	}
	
	    ]
	}), 201




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

	manager.add_viewdef(get_pin)


	#manager.add_viewdef(update_pin)

	manager.add_viewdef(update_board)
	manager.add_viewdef(get_comments)
	manager.add_viewdef(update_comment)
	manager.add_viewdef(get_comment)

	manager.add_viewdef(get_session_userId)
	manager.add_viewdef(get_sessions)

	manager.sync(app)
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

	app.run(host='0.0.0.0', port=5000)

	DB_URL = 'http://localhost:5984/pinboard'
    	#app.run(debug = True)
