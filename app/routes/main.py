from flask import Blueprint, render_template, request
from app.models import Route, Bus
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch unique source and destination cities for search dropdowns
    sources = db.session.query(Route.source).distinct().all()
    destinations = db.session.query(Route.destination).distinct().all()

    source_list = sorted([s[0] for s in sources])
    dest_list = sorted([d[0] for d in destinations])

    featured_buses = Bus.query.limit(6).all()
    routes_count = Route.query.count()
    buses_count = Bus.query.count()

    return render_template(
        'main/index.html',
        sources=source_list,
        destinations=dest_list,
        featured_buses=featured_buses,
        routes_count=routes_count,
        buses_count=buses_count
    )

@main_bp.route('/search')
def search():
    source = request.args.get('source', '').strip()
    destination = request.args.get('destination', '').strip()
    travel_date = request.args.get('travel_date', '')

    routes_query = Route.query
    if source:
        routes_query = routes_query.filter(Route.source.ilike(f'%{source}%'))
    if destination:
        routes_query = routes_query.filter(Route.destination.ilike(f'%{destination}%'))

    matching_routes = routes_query.all()
    route_ids = [r.id for r in matching_routes]

    available_buses = Bus.query.filter(Bus.route_id.in_(route_ids)).all() if route_ids else []

    all_sources = sorted([s[0] for s in db.session.query(Route.source).distinct().all()])
    all_destinations = sorted([d[0] for d in db.session.query(Route.destination).distinct().all()])

    return render_template(
        'main/search.html',
        buses=available_buses,
        source=source,
        destination=destination,
        travel_date=travel_date,
        all_sources=all_sources,
        all_destinations=all_destinations
    )

@main_bp.route('/routes')
def routes_list():
    all_routes = Route.query.all()
    return render_template('main/routes.html', routes=all_routes)
