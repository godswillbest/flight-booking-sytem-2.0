import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "flights.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (flight_id) REFERENCES flights(id)
    )''')
    
    conn.commit()
    
    # Create admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                       ('admin', hash_password('admin123'), 'Administrator', 'admin@system.com', 'admin'))
        conn.commit()
        print("✅ Admin user created")
    
    # Delete existing flights to add new Nigeria-focused routes
    cursor.execute("DELETE FROM flights")
    
    # Add Nigeria-focused sample flights
    sample_flights = [
        # === NIGERIA AIR ROUTES ===
        ('NG1001', 'Nigeria Air', 'Lagos', 'Abuja', '2025-06-20', '06:00', '07:30', 85000, 50, 50),
        ('NG1002', 'Nigeria Air', 'Abuja', 'Lagos', '2025-06-20', '08:00', '09:30', 85000, 50, 50),
        ('NG1003', 'Nigeria Air', 'Lagos', 'Port Harcourt', '2025-06-20', '10:00', '11:15', 65000, 40, 40),
        ('NG1004', 'Nigeria Air', 'Port Harcourt', 'Lagos', '2025-06-20', '12:00', '13:15', 65000, 40, 40),
        ('NG1005', 'Nigeria Air', 'Lagos', 'Kano', '2025-06-21', '07:00', '08:45', 70000, 45, 45),
        ('NG1006', 'Nigeria Air', 'Kano', 'Lagos', '2025-06-21', '09:30', '11:15', 70000, 45, 45),
        ('NG1007', 'Nigeria Air', 'Abuja', 'Port Harcourt', '2025-06-21', '14:00', '15:30', 60000, 35, 35),
        ('NG1008', 'Nigeria Air', 'Port Harcourt', 'Abuja', '2025-06-21', '16:00', '17:30', 60000, 35, 35),
        ('NG1009', 'Nigeria Air', 'Lagos', 'Enugu', '2025-06-22', '08:00', '09:15', 55000, 40, 40),
        ('NG1010', 'Nigeria Air', 'Enugu', 'Lagos', '2025-06-22', '10:00', '11:15', 55000, 40, 40),
        ('NG1011', 'Nigeria Air', 'Abuja', 'Kano', '2025-06-22', '12:00', '13:00', 50000, 35, 35),
        ('NG1012', 'Nigeria Air', 'Kano', 'Abuja', '2025-06-22', '14:00', '15:00', 50000, 35, 35),
        
        # === OTHER AIRLINES (African Routes) ===
        ('EK2001', 'Emirates', 'Lagos', 'Dubai', '2025-06-23', '10:00', '19:00', 450000, 80, 80),
        ('QR2002', 'Qatar Airways', 'Abuja', 'Doha', '2025-06-23', '11:00', '20:00', 420000, 75, 75),
        ('KQ2003', 'Kenya Airways', 'Lagos', 'Nairobi', '2025-06-24', '09:00', '14:30', 350000, 60, 60),
        ('ET2004', 'Ethiopian Airlines', 'Lagos', 'Addis Ababa', '2025-06-24', '13:00', '19:00', 320000, 65, 65),
        ('RW2005', 'RwandAir', 'Lagos', 'Kigali', '2025-06-25', '12:00', '16:30', 300000, 50, 50),
        ('SA2006', 'South African Airways', 'Lagos', 'Johannesburg', '2025-06-25', '14:00', '20:00', 400000, 70, 70),
        ('MK2007', 'Air Mauritius', 'Lagos', 'Mauritius', '2025-06-26', '15:00', '22:00', 480000, 55, 55),
    ]
    
    cursor.executemany("INSERT INTO flights (flight_number, airline, origin, destination, departure_date, departure_time, arrival_time, price, total_seats, available_seats) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sample_flights)
    conn.commit()
    print(f"✅ {len(sample_flights)} flights added to database!")
    
    conn.close()
    print("✅ Database setup complete!")

def check_user_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == "__main__":
    setup_database()