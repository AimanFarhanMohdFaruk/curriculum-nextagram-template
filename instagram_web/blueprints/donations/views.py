from flask import Blueprint, render_template, request, redirect, url_for, flash
from decimal import Decimal
from flask_login import login_required, current_user
from models.user_images import UserImages
from models.donate import Donation
from instagram_web.util.helpers import gateway, send_donation_email


donations_blueprint = Blueprint('donations',
                            __name__,
                            template_folder='templates')


@donations_blueprint.route('/<image_id>/new', methods=['GET'])
def new(image_id):
    token = gateway.client_token.generate()
    return render_template('donations/new.html', token=token, image_id = image_id)

@donations_blueprint.route("/<image_id>/donate", methods=["POST"])
def donate(image_id):
    nonce = request.form["nonce"]
    result = gateway.transaction.sale({
        "amount": "100.00",
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }   
    })
    if result.is_success:
        flash("Payment Received")
        send_donation_email()
        image = UserImages.get_by_id(image_id)
        donation = Donation(amount=Decimal(10) ,image=image)
        donation.save()
        return redirect(url_for('users.show', username= current_user.username))
    else:
        flash("Payment not successful")
        return redirect(url_for('users.show', username= current_user.username))
