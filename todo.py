import pymysql
from flask import Flask, request
from datetime import date
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import cached_property
from flaskext.mysql import MySQL
from functools import wraps

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sobhi'
app.config['MYSQL_DATABASE_DB'] = 'todo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'userid'
    }
}

app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
    authorizations=authorizations
)

def read_access(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        userid = None
        if 'userid' in request.headers:
            userid = request.headers['userid']
        if not userid:
            return {'message': 'User ID is missing!'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("select * from users where userid=%s", (userid))
            user = cursor.fetchall()
            if len(user) == 0:
                return {'message': 'Access Denied!'}, 401
        except Exception as e:
            print("Exception: ", e)
        finally:
            cursor.close()
            conn.close()
        return f(*args, **kwargs)
    return decorated

def write_access(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        userid = None
        if 'userid' in request.headers:
            userid = request.headers['userid']
        if not userid:
            return {'message': 'User ID is missing!'}, 400
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("select * from users where userid=%s", (userid))
            user = cursor.fetchall()
            if len(user) == 0 or (len(user) == 1 and user[0]['access'] != 'write'):
                    return {'message': 'Access Denied!'}, 401
        except Exception as e:
            print("Exception: ", e)
        finally:
            cursor.close()
            conn.close()
        return f(*args, **kwargs)
    return decorated
        

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by': fields.Date(required=True, description='The due date for the task'),
    'status': fields.String(required=True, description='The current status of the task (Not started, In progress, Finished)')
})


class TodoDAO(object):
    select = "select id, task, date_format(due_by, '%Y-%m-%d') as due_by, status from tasks"
    def __init__(self):
        try:
            self.conn = mysql.connect()
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            print("Exception: ", e)
            
    def __del__(self):
        self.cursor.close()
        self.conn.close()
        
    def getall(self):
        try:
            sts = self.cursor.execute(self.select)
            if sts > 0:
                return self.cursor.fetchall()
            return {'message': 'No Todos found'}, 404
        except Exception as e:
            print("Exception: ", e)

    def get(self, id):
        try:
            sts = self.cursor.execute(self.select+" where id={}".format(id))
            if sts > 0:
                return self.cursor.fetchone()
            return {'message': 'Todo {} not found'.format(id)}, 404
        except Exception as e:
            print("Exception: ", e)

    def create(self, data):
        try:
            self.cursor.execute("insert into tasks values(0, %s, %s, %s)", (data['task'], data['due_by'], data['status']))
            self.conn.commit()
            self.cursor.execute(self.select+" where id=(select last_insert_id() as id)")
            return self.cursor.fetchone(), 201
        except Exception as e:
            print("Exception: ", e)

    def update(self, id, data):
        try:
            sts = self.cursor.execute("update tasks set task=%s, due_by=%s, status=%s where id=%s", (data['task'], data['due_by'], data['status'], id))
            self.conn.commit()
            if sts == 0:
                return {'message': 'Todo {} not found'.format(id)}, 404
            return self.get(id)
        except Exception as e:
            print("Exception: ", e)

    def delete(self, id):
        try:
            sts = self.cursor.execute("delete from tasks where id=%s", (id))
            self.conn.commit()
            if sts == 0:
                return {'message': 'Todo {} not found'.format(id)}, 404
            return {'message': 'Successfully deleted'}
        except Exception as e:
            print("Exception: ", e)
        
    def updateStatus(self, id, status):
        try:
            sts = self.cursor.execute("update tasks set status=%s where id=%s", (status, id))
            self.conn.commit()
            if sts == 0:
                return {'message': 'Todo {} not found'.format(id)}, 404
            return self.get(id)
        except Exception as e:
            print("Exception: ", e)
    
    def getDue(self, due_by):
        try:
            print(due_by)
            sts = self.cursor.execute(self.select+" where due_by='{}'".format(due_by))
            if sts > 0:
                return self.cursor.fetchall()
            return {'message': 'No todos due on {}'.format(due_by)}, 404
        except Exception as e:
            print("Exception: ", e)
    
    def getOverdue(self):
        try:
            sts = self.cursor.execute(self.select+" where due_by<'{}'".format(date.today()))
            if sts > 0:
                return self.cursor.fetchall()
            return {'message': 'No Todos overdue as of today'}, 404
        except Exception as e:
            print("Exception: ", e)
    
    def getFinished(self):
        try:
            sts = self.cursor.execute(self.select+" where status like 'Finished'")
            if sts > 0:
                return self.cursor.fetchall()
            return {'message': 'No finished todos found'}, 404
        except Exception as e:
            print("Exception: ", e)


DAO = TodoDAO()
# DAO.create({'task': 'Build an API', 'due_by': '2022-11-01', 'status': 'In progress'})
# DAO.create({'task': 'marklist', 'due_by': '2022-11-19', 'status': 'Finished'})
# DAO.create({'task': 'Authorization', 'due_by': '2022-11-20', 'status': 'Not started'})


@ns.route('/')
@ns.response(201, 'Task created successfully')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'Empty Todo list')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @api.doc(security='apikey')
    @read_access
    @ns.doc('list_todos')
    # @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.getall()

    @api.doc(security='apikey')
    @write_access
    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload)


@ns.route('/<int:id>')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete and update them'''
    @api.doc(security='apikey')
    @read_access
    @ns.doc('get_todo')
    # @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given task given its identifier'''
        return DAO.get(id)

    @api.doc(security='apikey')
    @write_access
    @ns.doc('delete_todo')
    @ns.response(404, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        return DAO.delete(id)
    
    @api.doc(security='apikey')
    @write_access
    @ns.doc('update_todo')
    @ns.expect(todo)
    # @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)
    

@ns.route('/id=<int:id> status=<string:status>')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
@ns.param('status', 'The new status of the task')
class UpdateStatus(Resource):
    '''Lets you change the status of a task given its identifier'''
    @api.doc(security='apikey')
    @write_access
    @ns.doc('update_status')
    # @ns.marshal_list_with(todo)
    def put(self, id, status):
        '''Change the status of a task given its identifier'''
        return DAO.updateStatus(id, status)
    

@ns.route('/due/due_date=<string:due_by>')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'No tasks due')
@ns.param('due_by', 'Due Date')
class TasksDue(Resource):
    '''Show the tasks which are due on the given date'''
    @api.doc(security='apikey')
    @read_access
    @ns.doc('get_tasks_due')
    # @ns.marshal_list_with(todo)
    def get(self, due_by):
        '''Fetch the tasks due on the given date'''
        return DAO.getDue(due_by)
    
    
@ns.route('/overdue')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'No tasks overdue')
class TasksOverdue(Resource):
    '''Shows all the overdue tasks until today'''
    @api.doc(security='apikey')
    @read_access
    @ns.doc('get_tasks_overdue')
    # @ns.marshal_list_with(todo)
    def get(self):
        '''Fetch all overdue tasks'''
        return DAO.getOverdue()
    

@ns.route('/finished')
@ns.response(400, 'User ID is missing!')
@ns.response(401, 'Access Denied!')
@ns.response(404, 'No tasks finished')
class TasksFinished(Resource):
    '''Shows all the compeleted tasks'''
    @api.doc(security='apikey')
    @read_access
    @ns.doc('get_tasks_finished')
    # @ns.marshal_list_with(todo)
    def get(self):
        '''Fetchs all the finished tasks'''
        return DAO.getFinished()


if __name__ == '__main__':
    app.run(debug=True)