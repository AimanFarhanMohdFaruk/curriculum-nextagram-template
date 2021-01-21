from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from instagram_web.util.google_oauth import oauth

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
    else:
        flash("User does not exist, please try again.")
        return render_template("sessions/new.html")


@sessions_blueprint.route("/google_login")
def google_login():
    redirect_uri = url_for('sessions.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@sessions_blueprint.route("/authorize/google")
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user:
        login_user(user)
        return redirect('users.show', username = user.username)
    else:
        flash("Google account not found. Please log in with Nextagram username")
        return redirect('sessions.new')

@sessions_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('home'))
