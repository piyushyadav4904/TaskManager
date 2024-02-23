import logging
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_jwt_extended import JWTManager
from model import db
from config import ProductionConfig, DevelopmentConfig, StagingConfig
from logs import LoggingConfig
from view.login_view import UserLogin, UserRegister
from view.task_view import TaskResource
from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "error": {
                "class": "logging.FileHandler",
                "filename": "logs/error.log",
                "formatter": "default",
            },
        },

        "loggers": {
            "extra": {
                "level": "INFO",
                "handlers": ["error"],
                "propagate": False,
            }
        },
    }
)

extra = logging.getLogger("extra")

app = Flask(__name__)
# migrate = Migrate(app, db)
app.config.from_object(ProductionConfig)
jwt = JWTManager(app)
api = Api(app)


@app.errorhandler(404)
def not_found(error):
    extra.error("An error message")
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(401)
def unauthorized(error):
    # error_logger.error('Division by zero occurred!', exc_info=True)
    return jsonify({'error': 'Unauthorized'}), 401


api.add_resource(UserLogin, '/login')
api.add_resource(TaskResource, '/task', '/task/<int:task_id>')
api.add_resource(UserRegister, '/register')


def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
