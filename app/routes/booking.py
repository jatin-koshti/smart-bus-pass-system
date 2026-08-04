import uuid
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Bus, Ticket, BusPass, Payment
from app.utils.fare_calculator import calculate_ticket_fare
from app.utils.qr_generator import generate_qr_payload, generate_qr_base64

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/bus/<int:bus_id>', methods=['GET'])
@login_required
def select_seats(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    travel_date = request.args.get('travel_date', date.today().strftime('%Y-%m-%d'))

    # Fetch occupied seats for this bus and date
    booked_tickets = Ticket.query.filter_by(
        bus_id=bus_id, 
        travel_date=travel_date, 
        payment_status='SUCCESS'
    ).all()
    occupied_seats = [t.seat_number for t in booked_tickets]

    # Check if user has an active bus pass for discount
    active_pass = BusPass.query.filter_by(user_id=current_user.id, status='ACTIVE')\
        .filter(BusPass.valid_from <= date.today())\
        .filter(BusPass.valid_to >= date.today())\
        .first()

    estimated_fare = calculate_ticket_fare(
        distance_km=bus.route.distance_km,
        base_price=bus.route.base_price,
        bus_type=bus.bus_type,
        has_active_pass=bool(active_pass)
    )

    return render_template(
        'booking/seat_select.html',
        bus=bus,
        travel_date=travel_date,
        occupied_seats=occupied_seats,
        estimated_fare=estimated_fare,
        has_active_pass=bool(active_pass)
    )

@booking_bp.route('/checkout', methods=['POST'])
@login_required
def process_booking_checkout():
    bus_id = request.form.get('bus_id', type=int)
    seat_number = request.form.get('seat_number', '').strip()
    travel_date = request.form.get('travel_date', '').strip()

    if not bus_id or not seat_number or not travel_date:
        flash('Invalid booking details selected.', 'danger')
        return redirect(url_for('main.search'))

    bus = Bus.query.get_or_404(bus_id)

    # Prevent double booking
    already_booked = Ticket.query.filter_by(
        bus_id=bus_id,
        seat_number=seat_number,
        travel_date=travel_date,
        payment_status='SUCCESS'
    ).first()

    if already_booked:
        flash(f'Seat {seat_number} is already booked for {travel_date}. Please choose another seat.', 'warning')
        return redirect(url_for('booking.select_seats', bus_id=bus_id, travel_date=travel_date))

    # Calculate final fare
    active_pass = BusPass.query.filter_by(user_id=current_user.id, status='ACTIVE')\
        .filter(BusPass.valid_from <= date.today())\
        .filter(BusPass.valid_to >= date.today())\
        .first()

    fare = calculate_ticket_fare(
        distance_km=bus.route.distance_km,
        base_price=bus.route.base_price,
        bus_type=bus.bus_type,
        has_active_pass=bool(active_pass)
    )

    # Redirect to payment checkout route
    return redirect(url_for(
        'payment.checkout',
        item_type='TICKET',
        bus_id=bus.id,
        seat_number=seat_number,
        travel_date=travel_date,
        amount=fare
    ))

@booking_bp.route('/ticket/<string:ticket_code>')
@login_required
def ticket_details(ticket_code):
    ticket = Ticket.query.filter_by(ticket_code=ticket_code).first_or_404()

    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to ticket details.', 'danger')
        return redirect(url_for('main.index'))

    # Generate real-time Base64 QR Image
    qr_data_uri = generate_qr_base64(ticket.qr_token)

    return render_template(
        'booking/ticket_details.html',
        ticket=ticket,
        qr_data_uri=qr_data_uri
    )

@booking_bp.route('/my-tickets')
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.booked_at.desc()).all()
    return render_template('booking/my_tickets.html', tickets=tickets)

@booking_bp.route('/cancel/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized to cancel this ticket.', 'danger')
        return redirect(url_for('booking.my_tickets'))

    ticket.payment_status = 'CANCELLED'
    db.session.commit()
    flash(f'Ticket {ticket.ticket_code} has been cancelled.', 'info')
    return redirect(url_for('booking.my_tickets'))
