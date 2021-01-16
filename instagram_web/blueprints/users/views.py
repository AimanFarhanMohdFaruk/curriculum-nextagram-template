from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user



users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/create', methods=['POST'])
def create():
    params = request.form
    new_user = User(
        username = params.get('username'),
        email = params.get('email'),
        password = params.get('password')
    )
    if new_user.save():
        flash("User created")
        return redirect(url_for('home'))
    else:
        flash(new_user.errors)
        return redirect(url_for('users.new')) 

@users_blueprint.route('/<username>', methods=["GET"])
@login_required
def show(username):
    user = User.get_or_none(User.username == username)
    if user:
        return render_template("users/show.html", user=user)
    else:
        flash("User not found")
        return redirect(url_for("home"))


@users_blueprint.route('/', methods=["GET"])
def index():
    return "Hello World"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
