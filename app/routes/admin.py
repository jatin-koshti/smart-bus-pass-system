from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Route, Bus, Ticket, BusPass, Payment
from app.utils.qr_generator import verify_qr_payload

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access restricted to administrators only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='USER').count()
    total_buses = Bus.query.count()
    total_routes = Route.query.count()
    total_tickets = Ticket.query.count()
    total_passes = BusPass.query.count()
    
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'SUCCESS').scalar() or 0.0

    recent_tickets = Ticket.query.order_by(Ticket.booked_at.desc()).limit(5).all()
    recent_passes = BusPass.query.order_by(BusPass.purchased_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_buses=total_buses,
        total_routes=total_routes,
        total_tickets=total_tickets,
        total_passes=total_passes,
        total_revenue=total_revenue,
        recent_tickets=recent_tickets,
        recent_passes=recent_passes
    )

@admin_bp.route('/buses', methods=['GET', 'POST'])
@login_required
@admin_required
def buses():
    if request.method == 'POST':
        bus_name = request.form.get('bus_name', '').strip()
        bus_number = request.form.get('bus_number', '').strip().upper()
        route_id = request.form.get('route_id', type=int)
        total_seats = request.form.get('total_seats', type=int, default=40)
        bus_type = request.form.get('bus_type', 'Express')
        departure_time = request.form.get('departure_time', '08:00 AM')
        arrival_time = request.form.get('arrival_time', '12:00 PM')

        existing = Bus.query.filter_by(bus_number=bus_number).first()
        if existing:
            flash(f'Bus number {bus_number} already exists.', 'warning')
        else:
            new_bus = Bus(
                bus_name=bus_name,
                bus_number=bus_number,
                route_id=route_id,
                total_seats=total_seats,
                bus_type=bus_type,
                departure_time=departure_time,
                arrival_time=arrival_time
            )
            db.session.add(new_bus)
            db.session.commit()
            flash(f'Bus {bus_number} added successfully.', 'success')
            return redirect(url_for('admin.buses'))

    all_buses = Bus.query.all()
    all_routes = Route.query.all()
    return render_template('admin/buses.html', buses=all_buses, routes=all_routes)

@admin_bp.route('/buses/delete/<int:bus_id>', methods=['POST'])
@login_required
@admin_required
def delete_bus(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    db.session.delete(bus)
    db.session.commit()
    flash(f'Bus {bus.bus_number} deleted.', 'info')
    return redirect(url_for('admin.buses'))

@admin_bp.route('/routes', methods=['GET', 'POST'])
@login_required
@admin_required
def routes():
    if request.method == 'POST':
        source = request.form.get('source', '').strip().title()
        destination = request.form.get('destination', '').strip().title()
        distance_km = request.form.get('distance_km', type=float, default=50.0)
        base_price = request.form.get('base_price', type=float, default=100.0)
        estimated_duration = request.form.get('estimated_duration', '2 Hours')

        new_route = Route(
            source=source,
            destination=destination,
            distance_km=distance_km,
            base_price=base_price,
            estimated_duration=estimated_duration
        )
        db.session.add(new_route)
        db.session.commit()
        flash(f'Route {source} -> {destination} added.', 'success')
        return redirect(url_for('admin.routes'))

    all_routes = Route.query.all()
    return render_template('admin/routes.html', routes=all_routes)

@admin_bp.route('/routes/delete/<int:route_id>', methods=['POST'])
@login_required
@admin_required
def delete_route(route_id):
    route = Route.query.get_or_404(route_id)
    db.session.delete(route)
    db.session.commit()
    flash(f'Route {route.source} -> {route.destination} deleted.', 'info')
    return redirect(url_for('admin.routes'))

@admin_bp.route('/verify', methods=['GET', 'POST'])
@login_required
@admin_required
def verify():
    verification_result = None

    if request.method == 'POST':
        qr_token_or_code = request.form.get('token', '').strip()

        # Try to match direct code first (Ticket Code or Pass Code)
        ticket = Ticket.query.filter_by(ticket_code=qr_token_or_code).first()
        bus_pass = BusPass.query.filter_by(pass_code=qr_token_or_code).first()

        if ticket:
            is_valid, payload = verify_qr_payload(ticket.qr_token)
            verification_result = {
                "valid": is_valid and ticket.payment_status == 'SUCCESS',
                "type": "TICKET",
                "code": ticket.ticket_code,
                "user": ticket.user.full_name,
                "email": ticket.user.email,
                "seat": ticket.seat_number,
                "bus": f"{ticket.bus.bus_name} ({ticket.bus.bus_number})",
                "route": f"{ticket.route.source} -> {ticket.route.destination}",
                "travel_date": ticket.travel_date,
                "status": ticket.payment_status
            }
        elif bus_pass:
            is_valid, payload = verify_qr_payload(bus_pass.qr_token)
            verification_result = {
                "valid": is_valid and bus_pass.status == 'ACTIVE',
                "type": "BUS PASS",
                "code": bus_pass.pass_code,
                "user": bus_pass.user.full_name,
                "email": bus_pass.user.email,
                "pass_type": bus_pass.pass_type,
                "valid_from": str(bus_pass.valid_from),
                "valid_to": str(bus_pass.valid_to),
                "status": bus_pass.status
            }
        else:
            # Try parsing raw payload JSON
            is_valid, payload = verify_qr_payload(qr_token_or_code)
            if is_valid and payload:
                verification_result = {
                    "valid": True,
                    "type": payload.get('type'),
                    "code": payload.get('code'),
                    "details": payload
                }
            else:
                verification_result = {
                    "valid": False,
                    "message": "Invalid QR code payload or forged token detected!"
                }

    return render_template('admin/verify.html', result=verification_result)
