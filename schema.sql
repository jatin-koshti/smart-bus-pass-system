-- Raw SQL Schema for Smart Bus Pass & Ticket Booking System (PostgreSQL)

DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bus_passes CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS buses CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'USER' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance_km FLOAT NOT NULL,
    base_price FLOAT NOT NULL,
    estimated_duration VARCHAR(50) DEFAULT '2 Hours'
);

CREATE TABLE buses (
    id SERIAL PRIMARY KEY,
    bus_name VARCHAR(100) NOT NULL,
    bus_number VARCHAR(50) UNIQUE NOT NULL,
    route_id INT REFERENCES routes(id) ON DELETE CASCADE,
    total_seats INT DEFAULT 40 NOT NULL,
    bus_type VARCHAR(30) DEFAULT 'Express' NOT NULL,
    departure_time VARCHAR(20) NOT NULL,
    arrival_time VARCHAR(20) NOT NULL,
    price_multiplier FLOAT DEFAULT 1.0
);

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    ticket_code VARCHAR(64) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    bus_id INT REFERENCES buses(id) ON DELETE CASCADE,
    route_id INT REFERENCES routes(id) ON DELETE CASCADE,
    seat_number VARCHAR(10) NOT NULL,
    travel_date VARCHAR(20) NOT NULL,
    fare FLOAT NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'SUCCESS',
    qr_token TEXT NOT NULL,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bus_passes (
    id SERIAL PRIMARY KEY,
    pass_code VARCHAR(64) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    pass_type VARCHAR(20) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    fare FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    qr_token TEXT NOT NULL,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(64) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    amount FLOAT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'Credit Card',
    item_type VARCHAR(20) NOT NULL,
    item_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tickets_code ON tickets(ticket_code);
CREATE INDEX idx_passes_code ON bus_passes(pass_code);
