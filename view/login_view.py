import json
import re
from datetime import timedelta
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, jsonify, request
from model import User, db, Task
from werkzeug.security import generate_password_hash, check_password_hash


class UserLogin(Resource):

    def post(self):
        data_str = request.data.decode('utf-8').strip()
        data = json.loads(data_str)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"msg": "Missing username or password"}),

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user or not check_password_hash(existing_user.password, password):
            return jsonify({"msg": "Invalid username or password"})

        access_token = create_access_token(identity=existing_user.email, expires_delta=timedelta(hours=10))
        return {"access_token": access_token}, 200


class UserRegister(Resource):

    def post(self):
        data_str = request.data.decode('utf-8').strip()
        data = json.loads(data_str)
        full_name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        if not email or not password or not full_name:
            return jsonify({"msg": "Please add the required fields"})

        email_pattern = re.compile(r'^[\w-]+(\.[\w-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$')
        if not email_pattern.match(email):
            return jsonify({"msg": "Invalid email address"})

        if not len(password) > 8:  # Password length validation
            return jsonify({"msg": "Password must be at most 8 characters long"})

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"msg": "User already exists"})

        new_user = User(email=email, password=generate_password_hash(password), fullname=full_name)
        db.session.add(new_user)
        db.session.commit()
        return {"msg": "User added successfully"}, 201
