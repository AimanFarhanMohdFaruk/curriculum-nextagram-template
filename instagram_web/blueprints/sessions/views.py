from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user
from werkzeug.security import check_password_hash


sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')


@sessions_blueprint.route("/new", methods=['GET'])
def new():
    return render_template('sessions/new.html')

@sessions_blueprint.route("/", methods=['POST'])
def create():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.get_or_none(User.username == username)

    if user:
        result = check_password_hash(user.password_hash, password)

        if result:
            flash("Passwords matched!")

            login_user(user)
            return redirect(url_for('home'))
        
        else:
            flash("Password authentication failed, try again.")
            return render_template("sessions/new.html")