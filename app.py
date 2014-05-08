#!flask/bin/python
from flask import Flask, jsonify
from flask.ext.login import LoginManager
from couchdbkit.designer import push
#from couchdbkit.client.ViewResults import *
from couchdbkit import *
import datetime
#pip install pycurl
import pycurl
#apt-get install python-tk
import urllib
 



app = Flask(__name__)

login_manager = LoginManager(app)




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
server = Server()
class Greeting(Document):
	author = StringProperty()
      	content = StringProperty()
      	date = DateTimeProperty()
    		

def init_db(dburl):
	print 'Initializing', dburl
	db = server.get_or_create_db('greeting')
	print 'Created', db.dbname
    	
	
	Greeting.set_db(db)


	# create a new greet
	greet = Greeting(
   		author="Benoit",
    		content="Welcome to couchdbkit world",
    		date=datetime.datetime.utcnow()
	)

	# save it
	greet.save()

	push('/myproject/flask/lib/python2.7/site-packages/couchdbkit/example/_design/greeting', db)
 	greets = Greeting.view('greeting/all')
	#print greets
	#greetslist = list(greets) 
	#for greet in greetsList
	#	print greet['value']
		
	c = pycurl.Curl()
	url = 'http://localhost:5984/greeting/_design/greeting/_view/all'

	#params = {'q': 'stackoverflow answers'}

	c = pycurl.Curl()
	#c.setopt(c.URL, url + '?' + urllib.urlencode(params))
	c.setopt(c.URL, url)
	c.perform()



@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 401)



@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
@auth.login_required
def get_tasks():
    return jsonify( { 'tasks': tasks } )


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
	DB_URL = 'http://localhost:5984/greeting'
    	#init_db(DB_URL)
    	app.run(debug = True)
