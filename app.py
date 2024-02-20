from flask import Flask, jsonify, request
import json
import time
from datetime import timedelta
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@postgres:5432/TaskManager'  # Use your actual database URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:piyush%40123@localhost/TaskManager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a random secret key
db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def serialize(self):    # we can use marshmallow as well
        return {
            'id': self.id,
            'task': self.task,
            'user_id': self.user_id,
            'username': self.user.username
            # Add other fields as needed
        }


class UserLogin(Resource):

    def post(self):
        data_str = request.data.decode('utf-8').strip()
        data = json.loads(data_str)
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"msg": "Missing username or password"})

        # Check if user with the provided username already exists
        # need to check the password as well here do it docker things are done
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            existing_user = new_user
        access_token = create_access_token(identity=existing_user.username, expires_delta=timedelta(hours=10))
        return jsonify({"access_token": access_token, "status_code": 200})


class TaskResource(Resource):
    @jwt_required()
    def get(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error" : "task not found"}, 404
        return {'task': task.serialize()}, 201

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404
        db.session.delete(task)
        db.session.commit()
        return jsonify({'msg': "Task deleted successfully"})

    @jwt_required()
    def put(self, task_id):
        data_str = request.data.decode('utf-8').strip()
        data = json.loads(data_str)
        task_des = data['task']
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404
        task.task = task_des
        db.session.commit()
        return jsonify({'task': task.serialize()})


class TaskListResource(Resource):

    @jwt_required()
    def post(self):
        data_str = request.data.decode('utf-8').strip()
        data = json.loads(data_str)
        task_des = data['task']
        if not task_des:
            return {'message': 'Task description cannot be empty'}, 400
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        new_task = Task(task=data['task'], user=user)
        try:
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'task': new_task.serialize()})  # Return serialized task data
        except Exception as e:
            db.session.rollback()  # Revert changes on error
            return {'message': 'An error occurred creating the task'}, 500

    @jwt_required()
    def get(self):
        tasks = Task.query.all()
        serialize_task = [task.serialize() for task in tasks]
        return jsonify({'tasks': serialize_task})


# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401


# Add more error handlers as needed
api.add_resource(UserLogin, '/login')
api.add_resource(TaskResource, '/task/<int:task_id>')
api.add_resource(TaskListResource, '/task')


if __name__ == '__main__':
    with app.app_context():
        time.sleep(10)
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
