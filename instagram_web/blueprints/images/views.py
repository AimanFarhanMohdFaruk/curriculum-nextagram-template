from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user, current_user
from instagram_web.util.helpers import upload_file_to_s3
from werkzeug import secure_filename
from models.user_images import UserImages



images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')


@images_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('images/new.html')

@images_blueprint.route('/<id>/uploaduserimg', methods=['POST'])
@login_required
def upload_user_image(id):
    user = User.get_by_id(id)
    if user:
        if current_user.id == int(id):
            if "user_image" not in request.files:
                flash("No user_image key in request files.")
                return redirect(url_for('users.show', username = user.username))
            
            file = request.files["user_image"]

            file.filename= secure_filename(file.filename)

            image_path = upload_file_to_s3(file, user.username)

            image = UserImages(user_image_path= image_path, user = current_user.id)

            if image.save():
                return redirect(url_for('users.show', username = user.username))
            else:
                flash("Upload failed")
                return redirect(url_for('users.show', username = current_user.username))
        else:
            flash("Unauthorised to edit other user's profile")
            return redirect(url_for('sessions/new'))
    else:
        flash("User not found")
        return redirect(url_for('home'))
