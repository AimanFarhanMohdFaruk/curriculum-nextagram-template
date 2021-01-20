from flask import Blueprint, render_template, request, redirect, url_for, flash, session, escape
from models.user import User
from flask_login import login_required, login_user, current_user
from models.user_images import UserImages


donations_blueprint = Blueprint('donations',
                            __name__,
                            template_folder='templates')


@donations_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('donations/new.html')

@donations_blueprint.route('/show', methods=['GET'])
def show():
    token = gateway.client_token.generate()
    return render_template('donations/show.html', token=token)

@donations_blueprint.route("/donate", methods=["POST"])
def donate():
    nonce = request.form["nonce"]
    print("ITSSSSSS HEREEEEEEEEEEEEEE ====> " + nonce)
    result = gateway.transaction.sale({
        "amount": "100.00",
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }   
    })
    if result.is_success:
        flash("Payment Received")
        return redirect(url_for('users.show', username= current_user.username))
    else:
        return "Payment Failed"