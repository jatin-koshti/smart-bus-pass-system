# 🚌 Cloud-Based Smart Bus Pass & Ticket Booking System
> **CodeAlpha Cloud Computing Internship - Task 3**  
> Built with Python, Flask, SQLAlchemy, PostgreSQL/SQLite, Bootstrap 5, Flask-Login, Bcrypt, QR Code Generation, and Docker.

---

## 📌 Project Overview
The **Cloud-Based Smart Bus Pass & Ticket Booking System** is a production-grade, cloud-native web application designed to digitize public transit ticketing and bus pass management. It enables passengers to search bus routes, choose seats via an interactive grid, purchase daily/weekly/monthly bus passes with automated discounts, complete payments via a simulated gateway, and obtain cryptographically verified QR code tickets.

The system features a comprehensive **Admin & Conductor Portal** for real-time QR code verification, fleet management, and system revenue analytics.

---

## ✨ Features
- 🔐 **Secure Authentication & RBAC**: Flask-Login and Bcrypt salted password hashing with `USER` and `ADMIN` role access control.
- 🚌 **Bus & Route Search**: Filter by origin, destination, and bus service tiers (Express, AC, Sleeper, Non-AC).
- 💺 **Interactive Seat Picker**: Visual seat grid (2x2 seating layout) with real-time seat occupancy detection.
- 🎟️ **Digital Bus Passes**: Daily, Weekly, and Monthly bus passes auto-applying a 50% discount on single-ticket bookings.
- 📱 **Base64 QR Code Generation**: Downloadable & printable e-tickets with HMAC-SHA256 signature verification tokens.
- 💳 **Demo Payment Gateway**: Integrated checkout supporting Credit/Debit Cards, Net Banking, and Instant UPI.
- 🔍 **Verification Scanner**: Conductor portal to validate scanned QR codes and prevent ticket forgery.
- 📊 **Admin Dashboard**: Revenue statistics, booking lists, bus management, and route CRUD controls.
- 🐳 **Cloud-Native & Containerized**: Docker & Docker Compose support with PostgreSQL and SQLite dual compatibility.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.11, Flask 3.0, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF Protection)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism styling), Bootstrap 5.3, Bootstrap Icons, JavaScript (ES6)
- **Database**: PostgreSQL (Production) / SQLite 3 (Zero-setup local development)
- **QR Engine**: `qrcode`, `Pillow`, `hashlib` (HMAC-SHA256 Payload Signing)
- **DevOps**: Docker, Docker Compose, Gunicorn WSGI

---

## 🚀 Quick Local Setup

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Clone Repository & Environment Setup
```bash
git clone https://github.com/your-username/smart-bus-pass-system.git
cd smart-bus-pass-system

# Create virtual environment
python -m venv venv
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python seed_data.py
```

### 4. Run Application
```bash
python run.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## 🔑 Demo Credentials

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@smartbus.com` | `AdminPass123!` | Admin Panel, Fleet CRUD, QR Verifier, Revenue Stats |
| **Regular User** | `user@smartbus.com` | `UserPass123!` | Book Tickets, Buy Passes, QR E-Tickets |

---

## 🐳 Docker Deployment

Run the web application and PostgreSQL database with Docker Compose:
```bash
docker-compose up --build -d
```
Access the app at `http://localhost:5000`.

---

## 📡 REST API Endpoints

- `GET /api/v1/routes` - Retrieve all active network routes.
- `GET /api/v1/buses/<bus_id>/seats?date=YYYY-MM-DD` - Get seat availability for a given bus.
- `POST /api/v1/verify` - Programmatically verify QR payload tokens.

---

## 📂 Project Structure

```
smart-bus-pass-system/
├── app/
│   ├── __init__.py          # Flask app factory & blueprint registration
│   ├── config.py            # App & DB configuration
│   ├── extensions.py        # SQLAlchemy, Bcrypt, LoginManager, CSRF
│   ├── models.py            # User, Route, Bus, Ticket, BusPass, Payment models
│   ├── utils/
│   │   ├── qr_generator.py  # Base64 QR code generation & HMAC verification
│   │   └── fare_calculator.py # Distance & bus type dynamic pricing
│   ├── routes/
│   │   ├── auth.py          # User auth routes
│   │   ├── main.py          # Landing & route search
│   │   ├── booking.py       # Seat selection & ticket details
│   │   ├── passes.py        # Bus pass purchases
│   │   ├── payment.py       # Checkout & transaction simulation
│   │   ├── admin.py         # Dashboard, fleet CRUD, QR verifier
│   │   └── api.py           # REST API endpoints
│   ├── static/
│   │   ├── css/style.css    # Clean responsive CSS
│   │   └── js/main.js       # Interactive seat selector script
│   └── templates/           # Modular Jinja2 HTML templates
├── schema.sql               # PostgreSQL DDL script
├── seed_data.py             # Database seeder script
├── run.py                   # Server entrypoint
├── requirements.txt         # Dependencies list
├── Dockerfile               # Container spec
├── docker-compose.yml       # Web + DB orchestration
├── deployment_guide.md      # AWS/Azure/GCP scaling guide
└── README.md                # Documentation
```

---

## 📜 CodeAlpha Task 3 Requirements Checklist
- [x] Cloud-based smart bus pass & ticket booking application
- [x] Secure registration and login (Flask-Login + Bcrypt)
- [x] Bus route search and seat availability
- [x] Automatic fare calculation
- [x] Downloadable/printable QR code digital tickets
- [x] Daily, Weekly, and Monthly bus pass management
- [x] Demo payment gateway integration with transaction logging
- [x] Admin dashboard for managing buses, routes, users, and ticket verification
- [x] Modular folder structure & input validation with CSRF protection
- [x] Docker support, raw SQL schema, seed data script, and cloud deployment guide

---

## 📄 License
This project is open-source and created for educational and internship demonstration purposes under CodeAlpha Cloud Computing Task 3.
