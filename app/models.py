from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='USER', nullable=False) # 'USER', 'ADMIN'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tickets = db.relationship('Ticket', backref='user', lazy=True, cascade='all, delete-orphan')
    passes = db.relationship('BusPass', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False, index=True)
    destination = db.Column(db.String(100), nullable=False, index=True)
    distance_km = db.Column(db.Float, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    estimated_duration = db.Column(db.String(50), default='2 Hours')

    # Relationships
    buses = db.relationship('Bus', backref='route', lazy=True, cascade='all, delete-orphan')
    tickets = db.relationship('Ticket', backref='route', lazy=True)

    def __repr__(self):
        return f'<Route {self.source} -> {self.destination}>'


class Bus(db.Model):
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True)
    bus_name = db.Column(db.String(100), nullable=False)
    bus_number = db.Column(db.String(50), unique=True, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    total_seats = db.Column(db.Integer, default=40, nullable=False)
    bus_type = db.Column(db.String(30), default='Express', nullable=False) # 'Express', 'AC Standard', 'Non-AC Standard', 'Luxury Sleeper'
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    price_multiplier = db.Column(db.Float, default=1.0)

    tickets = db.relationship('Ticket', backref='bus', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Bus {self.bus_number} ({self.bus_name})>'


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    travel_date = db.Column(db.String(20), nullable=False)
    fare = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='SUCCESS') # 'SUCCESS', 'PENDING', 'CANCELLED'
    qr_token = db.Column(db.Text, nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ticket {self.ticket_code}>'


class BusPass(db.Model):
    __tablename__ = 'bus_passes'

    id = db.Column(db.Integer, primary_key=True)
    pass_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pass_type = db.Column(db.String(20), nullable=False) # 'DAILY', 'WEEKLY', 'MONTHLY'
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    fare = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='ACTIVE') # 'ACTIVE', 'EXPIRED', 'CANCELLED'
    qr_token = db.Column(db.Text, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BusPass {self.pass_code} ({self.pass_type})>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='Credit Card')
    item_type = db.Column(db.String(20), nullable=False) # 'TICKET', 'PASS'
    item_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='SUCCESS')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
