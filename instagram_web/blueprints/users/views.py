from flask import Blueprint, render_template, request, redirect, url_for
from models.user import User
from werkzeug.security import generate_password_hash



users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/create', methods=['POST'])
def create():
    user = User(
        username = request.form['username'],
        email = request.form['email'],
        password = request.form['password']
    )
    if user.save():
        print("User created")
        return redirect(url_for('users.new'))
    else:
        print("Error in creating user")
        return redirect(url_for('home'))
    

@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "Hello World"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
