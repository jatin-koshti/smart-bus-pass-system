from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import BusPass
from app.utils.fare_calculator import calculate_pass_fare
from app.utils.qr_generator import generate_qr_base64

passes_bp = Blueprint('passes', __name__, url_prefix='/passes')

@passes_bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_pass():
    if request.method == 'POST':
        pass_type = request.form.get('pass_type', 'DAILY').upper()
        start_date_str = request.form.get('start_date', date.today().strftime('%Y-%m-%d'))
        
        try:
            valid_from = date.fromisoformat(start_date_str)
        except ValueError:
            valid_from = date.today()

        if pass_type == 'DAILY':
            valid_to = valid_from
        elif pass_type == 'WEEKLY':
            valid_to = valid_from + timedelta(days=7)
        elif pass_type == 'MONTHLY':
            valid_to = valid_from + timedelta(days=30)
        else:
            pass_type = 'DAILY'
            valid_to = valid_from

        fare = calculate_pass_fare(pass_type)

        return redirect(url_for(
            'payment.checkout',
            item_type='PASS',
            pass_type=pass_type,
            valid_from=valid_from.strftime('%Y-%m-%d'),
            valid_to=valid_to.strftime('%Y-%m-%d'),
            amount=fare
        ))

    today_str = date.today().strftime('%Y-%m-%d')
    return render_template('passes/buy_pass.html', today_str=today_str)

@passes_bp.route('/pass/<string:pass_code>')
@login_required
def pass_details(pass_code):
    bus_pass = BusPass.query.filter_by(pass_code=pass_code).first_or_404()

    if bus_pass.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to pass details.', 'danger')
        return redirect(url_for('main.index'))

    qr_data_uri = generate_qr_base64(bus_pass.qr_token)

    return render_template(
        'passes/pass_details.html',
        bus_pass=bus_pass,
        qr_data_uri=qr_data_uri
    )

@passes_bp.route('/my-passes')
@login_required
def my_passes():
    user_passes = BusPass.query.filter_by(user_id=current_user.id).order_by(BusPass.purchased_at.desc()).all()
    today = date.today()
    return render_template('passes/my_passes.html', passes=user_passes, today=today)
