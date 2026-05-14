import sqlite3
import hashlib
import random
import string
from datetime import datetime, timedelta

DB_NAME = "flights.db"
WINDOW_SEAT_FEE = 5000
CURRENCY_RATES = {
    'NGN': 1.0,
    'USD': 0.0024,
    'EUR': 0.0022
}

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_future_date(days_from_today):
    return (datetime.now() + timedelta(days=days_from_today + 2)).strftime("%Y-%m-%d")

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
        return_flight_id INTEGER,
        passenger_name TEXT NOT NULL,
        passenger_age INTEGER NOT NULL,
        trip_type TEXT DEFAULT 'One-way',
        return_date TEXT,
        adults INTEGER DEFAULT 1,
        children INTEGER DEFAULT 0,
        infants INTEGER DEFAULT 0,
        payment_method TEXT DEFAULT 'Card',
        total_price REAL DEFAULT 0.0,
        booking_date TEXT NOT NULL,
        status TEXT DEFAULT 'confirmed',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(flight_id) REFERENCES flights(id),
        FOREIGN KEY(return_flight_id) REFERENCES flights(id)
    )''')
    
    conn.commit()

    # Ensure booking table has new columns when migrating from older versions
    cursor.execute("PRAGMA table_info(bookings)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    migration_columns = [
        ("trip_type", "TEXT DEFAULT 'One-way'"),
        ("return_date", "TEXT"),
        ("return_flight_id", "INTEGER"),
        ("adults", "INTEGER DEFAULT 1"),
        ("children", "INTEGER DEFAULT 0"),
        ("infants", "INTEGER DEFAULT 0"),
        ("payment_method", "TEXT DEFAULT 'Card'"),
        ("total_price", "REAL DEFAULT 0.0")
    ]
    for column_name, column_def in migration_columns:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column_name} {column_def}")
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
            ('NG1011', 'Air Peace', 'Abuja (ABV)', 'Kano (KAN)', day2, '08:30', '10:15', 72000, 45, 45),
            ('NG1012', 'Air Peace', 'Lagos (LOS)', 'Accra (ACC)', day3, '09:45', '12:15', 160000, 55, 55),
            ('NG1013', 'Air Peace', 'Abuja (ABV)', 'Dakar (DSS)', day7, '10:00', '13:45', 250000, 50, 50),
            ('NG1014', 'Arik Air', 'Lagos (LOS)', 'Cairo (CAI)', day7, '11:00', '17:30', 280000, 45, 45),
            ('NG1015', 'Arik Air', 'Lagos (LOS)', 'London (LHR)', day14, '20:00', '06:00', 550000, 60, 60),
            ('EK2001', 'Emirates', 'Lagos (LOS)', 'Dubai (DXB)', day7, '10:00', '19:00', 450000, 80, 80),
            ('QR2002', 'Qatar Airways', 'Abuja (ABV)', 'Doha (DOH)', day7, '11:00', '20:00', 420000, 75, 75),
            ('KQ2003', 'Kenya Airways', 'Lagos (LOS)', 'Nairobi (NBO)', day7, '09:00', '14:30', 350000, 60, 60),
            ('ET2004', 'Ethiopian Airlines', 'Lagos (LOS)', 'Addis Ababa (ADD)', day14, '13:00', '19:00', 320000, 65, 65),
            ('RW2005', 'RwandAir', 'Lagos (LOS)', 'Kigali (KGL)', day14, '12:00', '16:30', 300000, 50, 50),
            ('SA2006', 'South African Airways', 'Lagos (LOS)', 'Johannesburg (JNB)', day14, '14:00', '20:00', 400000, 70, 70),
            ('LH3001', 'Lufthansa', 'Frankfurt (FRA)', 'London (LHR)', day7, '08:00', '08:55', 220000, 70, 70),
            ('BA3002', 'British Airways', 'London (LHR)', 'Paris (CDG)', day7, '10:00', '12:20', 180000, 60, 60),
            ('AC3003', 'Air Canada', 'Toronto (YYZ)', 'New York (JFK)', day7, '09:00', '11:00', 280000, 75, 75),
            ('AA3004', 'American Airlines', 'New York (JFK)', 'Los Angeles (LAX)', day14, '13:00', '16:30', 420000, 80, 80),
            ('SQ3005', 'Singapore Airlines', 'Singapore (SIN)', 'Tokyo (NRT)', day14, '09:00', '17:30', 520000, 70, 70),
            ('CX3006', 'Cathay Pacific', 'Hong Kong (HKG)', 'Bangkok (BKK)', day14, '13:00', '15:30', 260000, 70, 70),
            ('AF3007', 'Air France', 'Paris (CDG)', 'Barcelona (BCN)', day7, '12:00', '14:05', 200000, 70, 70),
            ('TK3008', 'Turkish Airlines', 'Istanbul (IST)', 'London (LHR)', day7, '11:00', '13:30', 240000, 65, 65),
            ('EK3009', 'Emirates', 'Dubai (DXB)', 'Cape Town (CPT)', day14, '22:00', '05:30', 480000, 75, 75),
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


def get_distinct_airlines():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT airline FROM flights ORDER BY airline")
    airlines = [row[0] for row in cursor.fetchall()]
    conn.close()
    return airlines


def get_booking_by_ref(reference):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_ref = ?", (reference,))
    booking = cursor.fetchone()
    conn.close()
    return booking


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, role FROM users ORDER BY username")
    users = cursor.fetchall()
    conn.close()
    return users


def add_flight(flight_number, airline, origin, destination, departure_date, departure_time, arrival_time, price, total_seats):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO flights (flight_number, airline, origin, destination, departure_date, departure_time, arrival_time, price, total_seats, available_seats) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (flight_number, airline, origin, destination, departure_date, departure_time, arrival_time, price, total_seats, total_seats)
    )
    conn.commit()
    conn.close()


def search_available_flights(origin, destination, departure_date, seats_required=1,
                               min_price=0, max_price=1_000_000,
                               airline=None, seat_class=None, stops=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM flights WHERE origin = ? AND destination = ? AND departure_date = ? AND available_seats >= ?"
    params = [origin, destination, str(departure_date), seats_required]
    if airline:
        query += " AND airline = ?"
        params.append(airline)
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
    query += " ORDER BY price ASC"
    cursor.execute(query, tuple(params))
    flights = cursor.fetchall()
    conn.close()
    return flights


def create_booking(user_id, flight_id, passenger_name, passenger_age, trip_type='One-way', return_date=None,
                   adults=1, children=0, infants=0, payment_method='Card', total_price=0.0, return_flight_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    seats_required = adults + children + infants
    if seats_required <= 0:
        raise ValueError("Please book at least one passenger.")

    cursor.execute("SELECT available_seats FROM flights WHERE id = ?", (flight_id,))
    flight_row = cursor.fetchone()
    if not flight_row or flight_row[0] < seats_required:
        conn.close()
        raise ValueError("No available seats on this flight for the requested passenger count.")

    if return_flight_id is not None:
        cursor.execute("SELECT available_seats FROM flights WHERE id = ?", (return_flight_id,))
        return_row = cursor.fetchone()
        if not return_row or return_row[0] < seats_required:
            conn.close()
            raise ValueError("No available seats on the return flight for the requested passenger count.")

    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attempts = 0

    while True:
        if attempts >= 5:
            conn.close()
            raise ValueError("Unable to generate a unique booking reference. Please try again.")

        booking_ref = 'FLY' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        try:
            cursor.execute("""
                INSERT INTO bookings (booking_ref, user_id, flight_id, return_flight_id, passenger_name, passenger_age, trip_type,
                                      return_date, adults, children, infants, payment_method, total_price,
                                      booking_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed')
            """, (
                booking_ref, user_id, flight_id, return_flight_id, passenger_name, passenger_age,
                trip_type, return_date, adults, children, infants, payment_method,
                total_price, booking_date
            ))

            cursor.execute(
                "UPDATE flights SET available_seats = available_seats - ? WHERE id = ? AND available_seats >= ?",
                (seats_required, flight_id, seats_required)
            )
            if cursor.rowcount == 0:
                conn.rollback()
                raise ValueError("No available seats on this flight for the requested passenger count.")

            if return_flight_id is not None:
                cursor.execute(
                    "UPDATE flights SET available_seats = available_seats - ? WHERE id = ? AND available_seats >= ?",
                    (seats_required, return_flight_id, seats_required)
                )
                if cursor.rowcount == 0:
                    conn.rollback()
                    raise ValueError("No available seats on the return flight for the requested passenger count.")

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
            f.price,
            b.trip_type,
            b.return_date,
            b.adults,
            b.children,
            b.infants,
            b.total_price,
            b.payment_method,
            b.return_flight_id,
            rf.flight_number,
            rf.origin,
            rf.destination,
            rf.departure_date,
            rf.departure_time,
            rf.price
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        LEFT JOIN flights rf ON b.return_flight_id = rf.id
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
            b.trip_type,
            b.return_date,
            b.adults,
            b.children,
            b.infants,
            b.total_price,
            b.payment_method,
            b.return_flight_id,
            rf.flight_number,
            rf.origin,
            rf.destination,
            rf.departure_date,
            rf.departure_time,
            rf.price,
            u.username,
            u.full_name,
            u.email
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        LEFT JOIN flights rf ON b.return_flight_id = rf.id
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    bookings = cursor.fetchall()
    conn.close()
    return bookings

if __name__ == "__main__":
    setup_database()