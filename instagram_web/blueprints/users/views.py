from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user, current_user
from instagram_web.util.helpers import upload_file_to_s3
from werkzeug import secure_filename
from instagram_web.util.helpers import gateway


users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')

#CREATE NEW USER
@users_blueprint.route('/create', methods=['POST'])
def create():
    params = request.form
    new_user = User(
        username = params.get('username'),
        email = params.get('email'),
        password = params.get('password')
    )
    if new_user.save():
        login_user(new_user)
        flash("User created")
        return redirect(url_for('home'))
    else:
        flash(new_user.errors)
        return redirect(url_for('users.new')) 

#SHOW USER PROFILE
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

#EDIT USER PROFILE, USERNAME, PASSWORD, EMAIL PAGE
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

#FUNC TO UPDATE EDIT CHANGES
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

            private = params.get('private')
            if private == "True":
                user.private = True
            else:
                user.private = False
            
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

#FORM TO UPDATE USRE PROFILE IMG
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

#UPLOAD PROFILEIMG FUNCTION
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

# USERS FOLLOW FUNCTION
@users_blueprint.route('/<following_id>/follow', methods=['POST'])
@login_required
def follow(following_id):
    following = User.get_by_id(following_id)

    if current_user.follow(following):
        if current_user.follow_status(following).is_approved:
            flash(f"Successfully followed {following.username}!", "info")
        else:
            flash(f"Your request to follow {following.username} has been sent", "info")
        return redirect(url_for('users.show', username=following.username))
    else:
        flash("Unable to follow user", "danger")
        return render_template(url_for('users.show', username = current_user.username))

            
@users_blueprint.route('/<following_id>/unfollow', methods=["POST"])
@login_required
def unfollow(following_id):
    following = User.get_by_id(following_id)

    if current_user.unfollow(following):
        flash(f"You have unfollowed {following.username}", "primary")
        return redirect(url_for('home'))
    else:
        flash("Error occurred in unfollowing user", "danger")
        return redirect(url_for('users.show', username=current_user.username))

@users_blueprint.route('/request', methods = ["GET"])
@login_required
def show_request():
    return render_template("users/request.html")

@users_blueprint.route('/<follower_id>/approve', methods=["POST"])
@login_required
def approve(follower_id):
    follower = User.get_by_id(follower_id)

    if current_user.approve_requests(follower):
        flash(f"Approved follow request by {follower.username}", "info")
        return redirect(url_for('home'))
    else:
        flash("Error in approving follow request")
        return redirect(url_for('home'))
