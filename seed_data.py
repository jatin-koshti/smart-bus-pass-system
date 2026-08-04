from app import create_app
from app.extensions import db
from app.models import User, Route, Bus

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()

        # Seed Admin User
        admin = User.query.filter_by(email='admin@smartbus.com').first()
        if not admin:
            admin = User(
                full_name='System Admin',
                email='admin@smartbus.com',
                phone='+1 800 555 0199',
                role='ADMIN'
            )
            admin.set_password('AdminPass123!')
            db.session.add(admin)
            print("Seeded Admin User: admin@smartbus.com / AdminPass123!")

        # Seed Demo Regular User
        demo_user = User.query.filter_by(email='user@smartbus.com').first()
        if not demo_user:
            demo_user = User(
                full_name='Alex Johnson',
                email='user@smartbus.com',
                phone='+1 555 014 8822',
                role='USER'
            )
            demo_user.set_password('UserPass123!')
            db.session.add(demo_user)
            print("Seeded Demo User: user@smartbus.com / UserPass123!")

        # Seed Routes
        if Route.query.count() == 0:
            r1 = Route(source='New York', destination='Boston', distance_km=346.0, base_price=45.0, estimated_duration='4.5 Hours')
            r2 = Route(source='New York', destination='Washington DC', distance_km=365.0, base_price=50.0, estimated_duration='4.8 Hours')
            r3 = Route(source='Los Angeles', destination='San Francisco', distance_km=615.0, base_price=75.0, estimated_duration='6.5 Hours')
            r4 = Route(source='Chicago', destination='Detroit', distance_km=455.0, base_price=60.0, estimated_duration='5.0 Hours')
            
            db.session.add_all([r1, r2, r3, r4])
            db.session.commit()
            print("Seeded 4 Network Routes.")

            # Seed Buses
            b1 = Bus(bus_name='Empire Express', bus_number='BUS-101', route_id=r1.id, total_seats=40, bus_type='Express', departure_time='07:00 AM', arrival_time='11:30 AM')
            b2 = Bus(bus_name='Boston Shuttle AC', bus_number='BUS-102', route_id=r1.id, total_seats=36, bus_type='AC Standard', departure_time='02:00 PM', arrival_time='06:30 PM')
            b3 = Bus(bus_name='Capital Cruiser', bus_number='BUS-201', route_id=r2.id, total_seats=40, bus_type='Express', departure_time='08:30 AM', arrival_time='01:15 PM')
            b4 = Bus(bus_name='Pacific Luxury Liner', bus_number='BUS-301', route_id=r3.id, total_seats=32, bus_type='Luxury Sleeper', departure_time='09:00 PM', arrival_time='03:30 AM')
            b5 = Bus(bus_name='Midwest Superliner', bus_number='BUS-401', route_id=r4.id, total_seats=40, bus_type='Non-AC Standard', departure_time='10:00 AM', arrival_time='03:00 PM')

            db.session.add_all([b1, b2, b3, b4, b5])
            db.session.commit()
            print("Seeded 5 Fleet Buses.")

        print("Database seed complete successfully!")

if __name__ == '__main__':
    seed_database()
