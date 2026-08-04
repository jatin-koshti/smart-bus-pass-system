import unittest
from app import create_app
from app.extensions import db
from app.models import User, Route, Bus, Ticket, BusPass
from datetime import date, timedelta

class TestBusBookingSystem(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Seed test data
            self.seed_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_test_data(self):
        # Seed test admin
        admin = User(full_name="Admin Test", email="admin@test.com", role="ADMIN")
        admin.set_password("adminpass")
        db.session.add(admin)
        
        # Seed test user
        user = User(full_name="User Test", email="user@test.com", role="USER")
        user.set_password("userpass")
        db.session.add(user)
        
        # Seed test route
        route = Route(source="New York", destination="Boston", distance_km=340.0, base_price=50.0)
        db.session.add(route)
        db.session.commit()
        
        # Seed test bus
        bus = Bus(bus_name="Test Shuttle", bus_number="TST-101", route_id=route.id, 
                  total_seats=40, bus_type="Express", departure_time="09:00 AM", arrival_time="01:00 PM")
        db.session.add(bus)
        db.session.commit()

    def login(self, email, password):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New York', response.data)
        self.assertIn(b'Boston', response.data)

    def test_search(self):
        response = self.client.get('/search?source=New+York&destination=Boston')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Shuttle', response.data)

    def test_routes_list(self):
        response = self.client.get('/routes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New York', response.data)
        self.assertIn(b'Boston', response.data)

    def test_login_logout(self):
        # Test login page GET
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

        # Test login POST
        response = self.login('user@test.com', 'userpass')
        self.assertIn(b'User Test', response.data)

        # Test logout
        response = self.logout()
        self.assertIn(b'You have been logged out successfully.', response.data)

    def test_registration(self):
        response = self.client.post('/auth/register', data=dict(
            full_name="New Passenger",
            email="passenger@test.com",
            phone="1234567890",
            password="pass123password",
            confirm_password="pass123password"
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful! Please sign in.', response.data)

    def test_booking_flow(self):
        # Login first
        self.login('user@test.com', 'userpass')
        
        # Access seat selection
        response = self.client.get('/booking/bus/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Shuttle', response.data)

        # Test checkout page redirect/get
        response = self.client.get('/payment/checkout?item_type=TICKET&bus_id=1&seat_number=S12&travel_date=2026-08-10&amount=55.0')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Demo Payment Checkout', response.data)

        # Test process payment POST
        response = self.client.post('/payment/process', data=dict(
            item_type='TICKET',
            payment_method='Credit Card',
            amount=55.0,
            bus_id=1,
            seat_number='S12',
            travel_date='2026-08-10'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Payment successful! Ticket booked.', response.data)

    def test_pass_flow(self):
        self.login('user@test.com', 'userpass')
        
        # Access pass page
        response = self.client.get('/passes/buy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Choose Your Smart Bus Pass', response.data)

        # Process payment for pass
        response = self.client.post('/payment/process', data=dict(
            item_type='PASS',
            payment_method='Credit Card',
            amount=150.0,
            pass_type='DAILY',
            valid_from=date.today().strftime('%Y-%m-%d'),
            valid_to=date.today().strftime('%Y-%m-%d')
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Payment successful! Bus pass activated.', response.data)

    def test_admin_dashboard(self):
        # Access admin unauthorized
        self.login('user@test.com', 'userpass')
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access restricted to administrators only.', response.data)
        
        # Logout
        self.logout()
        
        # Access admin authorized
        self.login('admin@test.com', 'adminpass')
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin System Dashboard', response.data)

if __name__ == '__main__':
    unittest.main()
