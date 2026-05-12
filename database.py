import sqlite3
import hashlib
import random
import string
from datetime import datetime, timedelta

DB_NAME = "flights.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_future_date(days_from_today):
    return (datetime.now() + timedelta(days=days_from_today)).strftime("%Y-%m-%d")

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )''')
    
    # Flights table
    cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT UNIQUE NOT NULL,
        airline TEXT NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        price REAL NOT NULL,
        total_seats INTEGER NOT NULL,
        available_seats INTEGER NOT NULL
    )''')
    
    # Bookings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        flight_id INTEGER NOT NULL,
        passenger_name TEXT NOT NULL,
        passenger_age INTEGER NOT NULL,
        booking_date TEXT NOT NULL,
        status TEXT DEFAULT 'confirmed',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(flight_id) REFERENCES flights(id)
    )''')
    
    conn.commit()
    
    # Create admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                       ('admin', hash_password('admin123'), 'System Administrator', 'admin@flightbookingsystem.com', 'admin'))
        conn.commit()
        print("Admin user created (username: admin, password: admin123)")
    
    # Add sample flights if none exist
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] == 0:
        day1 = get_future_date(1)
        day2 = get_future_date(2)
        day3 = get_future_date(3)
        day7 = get_future_date(7)
        day14 = get_future_date(14)
        
        flights = [
            # Nigeria Domestic Routes
            ('NG1001', 'Nigeria Air', 'Lagos (LOS)', 'Abuja (ABV)', day1, '06:00', '07:30', 85000, 50, 50),
            ('NG1002', 'Nigeria Air', 'Abuja (ABV)', 'Lagos (LOS)', day1, '08:00', '09:30', 85000, 50, 50),
            ('NG1003', 'Nigeria Air', 'Lagos (LOS)', 'Port Harcourt (PHC)', day2, '10:00', '11:15', 65000, 40, 40),
            ('NG1004', 'Nigeria Air', 'Port Harcourt (PHC)', 'Lagos (LOS)', day2, '12:00', '13:15', 65000, 40, 40),
            ('NG1005', 'Nigeria Air', 'Lagos (LOS)', 'Kano (KAN)', day3, '07:00', '08:45', 70000, 45, 45),
            ('NG1006', 'Nigeria Air', 'Kano (KAN)', 'Lagos (LOS)', day3, '09:30', '11:15', 70000, 45, 45),
            ('NG1007', 'Nigeria Air', 'Abuja (ABV)', 'Port Harcourt (PHC)', day7, '14:00', '15:30', 60000, 35, 35),
            ('NG1008', 'Nigeria Air', 'Port Harcourt (PHC)', 'Abuja (ABV)', day7, '16:00', '17:30', 60000, 35, 35),
            ('NG1009', 'Nigeria Air', 'Lagos (LOS)', 'Enugu (ENU)', day14, '08:00', '09:15', 55000, 40, 40),
            ('NG1010', 'Nigeria Air', 'Enugu (ENU)', 'Lagos (LOS)', day14, '10:00', '11:15', 55000, 40, 40),
            
            # International Routes
            ('EK2001', 'Emirates', 'Lagos (LOS)', 'Dubai (DXB)', day7, '10:00', '19:00', 450000, 80, 80),
            ('QR2002', 'Qatar Airways', 'Abuja (ABV)', 'Doha (DOH)', day7, '11:00', '20:00', 420000, 75, 75),
            ('KQ2003', 'Kenya Airways', 'Lagos (LOS)', 'Nairobi (NBO)', day7, '09:00', '14:30', 350000, 60, 60),
            ('ET2004', 'Ethiopian Airlines', 'Lagos (LOS)', 'Addis Ababa (ADD)', day14, '13:00', '19:00', 320000, 65, 65),
            ('RW2005', 'RwandAir', 'Lagos (LOS)', 'Kigali (KGL)', day14, '12:00', '16:30', 300000, 50, 50),
            ('SA2006', 'South African Airways', 'Lagos (LOS)', 'Johannesburg (JNB)', day14, '14:00', '20:00', 400000, 70, 70),
        ]
        
        cursor.executemany("""
            INSERT INTO flights (flight_number, airline, origin, destination, departure_date, 
                               departure_time, arrival_time, price, total_seats, available_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, flights)
        conn.commit()
        print(f"Added {len(flights)} flights successfully!")
    
    conn.close()
    print("Database setup complete!")

def get_all_flights():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights ORDER BY departure_date")
    flights = cursor.fetchall()
    conn.close()
    return flights


def get_flight_by_id(flight_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    flight = cursor.fetchone()
    conn.close()
    return flight


def search_available_flights(origin, destination, departure_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM flights 
        WHERE origin = ? AND destination = ? AND departure_date = ? AND available_seats > 0
        ORDER BY price ASC
    """, (origin, destination, str(departure_date)))
    flights = cursor.fetchall()
    conn.close()
    return flights


def create_booking(user_id, flight_id, passenger_name, passenger_age):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT available_seats FROM flights WHERE id = ?", (flight_id,))
    flight_row = cursor.fetchone()
    if not flight_row or flight_row[0] <= 0:
        conn.close()
        raise ValueError("No available seats on this flight. Please choose another flight.")

    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attempts = 0

    while True:
        if attempts >= 5:
            conn.close()
            raise ValueError("Unable to generate a unique booking reference. Please try again.")

        booking_ref = 'FLY' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        try:
            cursor.execute("""
                INSERT INTO bookings (booking_ref, user_id, flight_id, passenger_name, passenger_age, booking_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
            """, (booking_ref, user_id, flight_id, passenger_name, passenger_age, booking_date))

            cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = ? AND available_seats > 0", (flight_id,))
            if cursor.rowcount == 0:
                conn.rollback()
                raise ValueError("No available seats on this flight. Please choose another flight.")

            conn.commit()
            return booking_ref
        except sqlite3.IntegrityError:
            conn.rollback()
            attempts += 1
        except Exception:
            conn.rollback()
            conn.close()
            raise


def get_user_bookings(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            b.booking_ref,
            b.passenger_name,
            b.passenger_age,
            b.booking_date,
            b.status,
            f.flight_number,
            f.airline,
            f.origin,
            f.destination,
            f.departure_date,
            f.departure_time,
            f.price
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.user_id = ?
        ORDER BY b.booking_date DESC
    """, (user_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings


def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            b.booking_ref,
            b.passenger_name,
            b.passenger_age,
            b.booking_date,
            b.status,
            f.flight_number,
            f.airline,
            f.origin,
            f.destination,
            f.departure_date,
            f.departure_time,
            f.price,
            u.username,
            u.full_name,
            u.email
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    bookings = cursor.fetchall()
    conn.close()
    return bookings

if __name__ == "__main__":
    setup_database()