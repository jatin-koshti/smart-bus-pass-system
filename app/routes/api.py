from flask import Blueprint, jsonify, request
from app.models import Route, Bus, Ticket, BusPass
from app.utils.qr_generator import verify_qr_payload

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/routes', methods=['GET'])
def get_routes():
    routes = Route.query.all()
    data = [{
        "id": r.id,
        "source": r.source,
        "destination": r.destination,
        "distance_km": r.distance_km,
        "base_price": r.base_price,
        "estimated_duration": r.estimated_duration
    } for r in routes]
    return jsonify({"success": True, "count": len(data), "routes": data})

@api_bp.route('/buses/<int:bus_id>/seats', methods=['GET'])
def get_seat_availability(bus_id):
    travel_date = request.args.get('date')
    bus = Bus.query.get(bus_id)
    if not bus:
        return jsonify({"success": False, "error": "Bus not found"}), 404

    tickets = Ticket.query.filter_by(bus_id=bus_id, travel_date=travel_date, payment_status='SUCCESS').all()
    occupied_seats = [t.seat_number for t in tickets]

    return jsonify({
        "success": True,
        "bus_id": bus.id,
        "bus_number": bus.bus_number,
        "total_seats": bus.total_seats,
        "occupied_count": len(occupied_seats),
        "occupied_seats": occupied_seats,
        "available_seats": bus.total_seats - len(occupied_seats)
    })

@api_bp.route('/verify', methods=['POST'])
def verify_qr():
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({"success": False, "error": "Missing token parameter"}), 400

    is_valid, payload = verify_qr_payload(token)
    return jsonify({
        "valid": is_valid,
        "payload": payload
    })
