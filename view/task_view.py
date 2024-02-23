import json
import logging

from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from model import Task, User, db

extra = logging.getLogger("extra")


class TaskResource(Resource):
    @jwt_required()
    def get(self, task_id=None):
        try:
            if task_id is None:
                tasks = Task.query.all()
                serialize_task = [task.serialize() for task in tasks]
                return jsonify({'tasks': serialize_task})
            else:
                task = Task.query.get(task_id)
                if not task:
                    return {"error": "Task not found"}, 404
                return {'task': task.serialize()}, 200
        except Exception as e:
            extra.error("An error occurred while retrieving tasks")
            return {'message': 'An error occurred while retrieving tasks'}, 500

    @jwt_required()
    def post(self):
        try:
            data_str = request.data.decode('utf-8').strip()
            data = json.loads(data_str)
            task_des = data.get('task')
            if not task_des:
                return {'message': 'Task description cannot be empty'}, 400
            username = get_jwt_identity()
            user = User.query.filter_by(email=username).first()
            new_task = Task(task=task_des, user=user)
            db.session.add(new_task)
            db.session.commit()
            return {'task': new_task.serialize()}, 201
        except Exception as e:
            db.session.rollback()
            extra.error("An error occurred creating the task")
            return {'message': 'An error occurred creating the task'}, 500

    @jwt_required()
    def put(self, task_id):
        try:
            data_str = request.data.decode('utf-8').strip()
            data = json.loads(data_str)
            task_des = data.get('task')
            task = Task.query.get(task_id)
            if not task:
                return {"error": "Task not found"}, 404
            task.task = task_des
            db.session.commit()
            return jsonify({'task': task.serialize()})
        except Exception as e:
            db.session.rollback()
            extra.error("An error occurred while updating the task")
            return {'message': 'An error occurred while updating the task'}, 500

    @jwt_required()
    def delete(self, task_id):
        try:
            task = Task.query.get(task_id)
            if not task:
                return {"error": "Task not found"}, 404
            db.session.delete(task)
            db.session.commit()
            return jsonify({'msg': "Task deleted successfully"})
        except Exception as e:
            db.session.rollback()
            extra.error("An error occurred while deleting the task")
            return {'message': 'An error occurred while deleting the task'}, 500