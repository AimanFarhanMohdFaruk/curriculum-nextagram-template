from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models.user import User

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['POST'])
def create():
    params = request.json
    new_user = User(username = params.get("username"), email=params.get("email"), password=params.get("password"))

    if new_user.save():
        token = create_access_token(identity = new_user.id)
        return jsonify({"token":token})
    else:
        return jsonify([err for err in new_user.errors])