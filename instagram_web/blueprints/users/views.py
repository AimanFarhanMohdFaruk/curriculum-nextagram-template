from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user, current_user
from instagram_web.util.helpers import upload_file_to_s3
from werkzeug import secure_filename
from models import user_images

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
    user = User.get_by_id(id)
    
    if user:
        if current_user == user:
            return render_template('users/edit.html', user=user) 
        else:
            flash("Unable to edit other user's profiles.")
            return redirect(url_for('users.show'))
    else:
        flash("User not found")
        return redirect(url_for('home'))

@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    user = User.get_or_none(User.id == id)

    if user:
        if current_user.id == int(id):
            params = request.form

            user.username = params.get('username')
            user.email = params.get('email')

            password = params.get('password')
            if len(password) > 0:
                user.password = password
            
            if user.save():
                flash("Successfully update profile information")
                return redirect(url_for("users.show", username = user.username))
            else:
                flash("Failed to edit, try again.")
                return redirect (url_for("users.edit", id = user.id))
        else:
            flash("You are not authorised to edit other user's profiles.")
            return redirect(url_for("home"))
    else:
        flash("User not found")
        return redirect(url_for("home"))


@users_blueprint.route('/<id>/profileimg', methods=["GET"])
def profileimg(id):
    user = User.get_by_id(id)
    if user:
        if current_user.id == int(id):
            return render_template("users/profileimg.html", user=user)
        else:
            redirect(url_for('sessions.new'))
    else:
        return redirect('home')

@users_blueprint.route('/<id>/create', methods=['POST'])
@login_required
def upload_file(id):
    user = User.get_by_id(id)
    if user:
        if current_user.id == int(id):
            if "profile_image" not in request.files:
                flash("No profile_image key in request files.")
                return redirect(url_for('users.profileimg', id = user.id))
            
            file = request.files["profile_image"]

            file.filename= secure_filename(file.filename)

            image_path = upload_file_to_s3(file, user.username)

            user.image_path = image_path

            if user.save():
                return redirect(url_for('users.show', username = user.username))
                
            else:
                flash("Upload failed")
                return redirect(url_for('users.show', username = user.username))
        else:
            flash("Unauthorised to edit other user's profile")
            return redirect(url_for('sessions.new'))
    else:
        flash("User not found")
        return redirect(url_for('home'))

# @users_blueprint.route('/<id>/uploaduserimg', methods=['POST'])
# @login_required
# def upload_user_image(id):
#     user = User.get_by_id(id)
#     if user:
#         if current_user.id == int(id):
#             if "user_image" not in request.files:
#                 flash("No user_image key in request files.")
#                 return redirect(url_for('users.show', username = user.username))
            
#             file = request.files["user_image"]

#             file.filename= secure_filename(file.filename)

#             image_path = upload_file_to_s3(file, user.username)

#             user_images.image_path = image_path
#             user_images.user = user

#             if user_images.save():
#                 return redirect(url_for('users.show', username = user.username))
#             else:
#                 flash("Upload failed")
#                 return redirect(url_for('users.show', username = user.username))
#         else:
#             flash("Unauthorised to edit other user's profile")
#             return redirect(url_for('sessions/new'))
#     else:
#         flash("User not found")
#         return redirect(url_for('home'))
            
