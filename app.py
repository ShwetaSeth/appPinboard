#!flask/bin/python
from flask import Flask, jsonify, g, request,session, redirect, url_for, escape
from flask.ext.login import LoginManager
import datetime
#pip install pycurl
#import pycurl
#apt-get install python-tk
#import urllib
from documents import User
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

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

#curl -i -H "Content-Type: application/json" -X POST -d '{"firstname":"Bharat","lastname":"Mehndiratta","username":"bharat","password":"bharat16"}' http://localhost:5000/signup
@app.route('/signup', methods = ['POST'])
def signup():
	register(request.json['firstname'],request.json['lastname'],request.json['username'],request.json['password'])
	return jsonify( { 'Sign Up Message': 'Sign up Successfull' } )


@auth.verify_password
def verify_password(username, password):
	return checkPass(username,password)

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 401)

#curl -u bharat:bharat16 -i http://localhost:5000/login
@app.route('/login', methods = ['GET'])
@auth.login_required
def get_tasks():
	flask.ext.login.confirm_login()
	#user = getuser
	#flask.ext.login.login_user(user)
   	return jsonify( { 'Log In Message': 'Log in Successfull' } )


@app.route("/logout")
@auth.login_required
def logout():
    flask.ext.login.logout_user()
    return jsonify( { 'Log out Message': 'Log out Successfull' } )
	
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

from flask import request
@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)


	
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify( { 'task': task } ), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['PUT'])
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify( { 'task': task[0] } )


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify( { 'result': True } )

if __name__ == '__main__':
	app.config.update(
        	DEBUG = True,
        	COUCHDB_SERVER = 'http://localhost:5984/',
        	COUCHDB_DATABASE = 'pinboard'
    	)
   	manager = flask.ext.couchdb.CouchDBManager()
    	manager.setup(app)
    	manager.add_viewdef(get_passwords)  # Install the view
    	manager.sync(app)

	app.run(host='0.0.0.0', port=5000)

	DB_URL = 'http://localhost:5984/pinboard'
    	#app.run(debug = True)
