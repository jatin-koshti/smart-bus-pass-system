import uuid
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Ticket, BusPass, Payment, Bus
from app.utils.qr_generator import generate_qr_payload

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

@payment_bp.route('/checkout')
@login_required
def checkout():
    item_type = request.args.get('item_type', 'TICKET')
    amount = request.args.get('amount', type=float, default=100.0)

    bus = None
    if item_type == 'TICKET':
        bus_id = request.args.get('bus_id', type=int)
        bus = Bus.query.get(bus_id) if bus_id else None

    return render_template(
        'payment/checkout.html',
        item_type=item_type,
        amount=amount,
        bus=bus,
        seat_number=request.args.get('seat_number'),
        travel_date=request.args.get('travel_date'),
        pass_type=request.args.get('pass_type'),
        valid_from=request.args.get('valid_from'),
        valid_to=request.args.get('valid_to')
    )

@payment_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    item_type = request.form.get('item_type', 'TICKET')
    payment_method = request.form.get('payment_method', 'Credit Card')
    amount = request.form.get('amount', type=float, default=0.0)

    # Generate mock transaction reference ID
    txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

    if item_type == 'TICKET':
        bus_id = request.form.get('bus_id', type=int)
        seat_number = request.form.get('seat_number')
        travel_date = request.form.get('travel_date')

        bus = Bus.query.get_or_404(bus_id)
        ticket_code = f"TCK-{uuid.uuid4().hex[:8].upper()}"

        # Build cryptographic QR token payload
        payload_data = {
            "type": "TICKET",
            "code": ticket_code,
            "user_email": current_user.email,
            "bus_number": bus.bus_number,
            "seat": seat_number,
            "date": travel_date,
            "route": f"{bus.route.source} -> {bus.route.destination}"
        }
        qr_token = generate_qr_payload(payload_data)

        new_ticket = Ticket(
            ticket_code=ticket_code,
            user_id=current_user.id,
            bus_id=bus.id,
            route_id=bus.route_id,
            seat_number=seat_number,
            travel_date=travel_date,
            fare=amount,
            payment_status='SUCCESS',
            qr_token=qr_token
        )
        db.session.add(new_ticket)
        db.session.flush() # get ticket.id

        payment_rec = Payment(
            transaction_id=txn_id,
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            item_type='TICKET',
            item_id=new_ticket.id,
            status='SUCCESS'
        )
        db.session.add(payment_rec)
        db.session.commit()

        flash(f'Payment successful! Ticket booked. Transaction ID: {txn_id}', 'success')
        return redirect(url_for('booking.ticket_details', ticket_code=ticket_code))

    elif item_type == 'PASS':
        pass_type = request.form.get('pass_type', 'DAILY')
        valid_from_str = request.form.get('valid_from')
        valid_to_str = request.form.get('valid_to')

        valid_from = date.fromisoformat(valid_from_str) if valid_from_str else date.today()
        valid_to = date.fromisoformat(valid_to_str) if valid_to_str else date.today()

        pass_code = f"PSS-{uuid.uuid4().hex[:8].upper()}"

        payload_data = {
            "type": "PASS",
            "code": pass_code,
            "pass_type": pass_type,
            "user_email": current_user.email,
            "valid_from": valid_from.strftime('%Y-%m-%d'),
            "valid_to": valid_to.strftime('%Y-%m-%d')
        }
        qr_token = generate_qr_payload(payload_data)

        new_pass = BusPass(
            pass_code=pass_code,
            user_id=current_user.id,
            pass_type=pass_type,
            valid_from=valid_from,
            valid_to=valid_to,
            fare=amount,
            status='ACTIVE',
            qr_token=qr_token
        )
        db.session.add(new_pass)
        db.session.flush()

        payment_rec = Payment(
            transaction_id=txn_id,
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method,
            item_type='PASS',
            item_id=new_pass.id,
            status='SUCCESS'
        )
        db.session.add(payment_rec)
        db.session.commit()

        flash(f'Payment successful! Bus pass activated. Transaction ID: {txn_id}', 'success')
        return redirect(url_for('passes.pass_details', pass_code=pass_code))

    flash('Payment failed or unknown item type.', 'danger')
    return redirect(url_for('main.index'))
