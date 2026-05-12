import os
import sqlite3
import database as db

TEST_DB = "test_flights.db"


def setup_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.DB_NAME = TEST_DB
    db.setup_database()


def test_search_flights_returns_available_flights():
    flights = db.search_available_flights('Lagos (LOS)', 'Abuja (ABV)', db.get_future_date(1))
    assert isinstance(flights, list), 'Expected list of flights'
    assert len(flights) > 0, 'Expected at least one available flight for Lagos to Abuja tomorrow'
    return flights[0]


def test_create_booking_reduces_seats_and_returns_ref(flight_id):
    # Create a new test user
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, 'user')",
                   ('testuser', db.hash_password('testpass'), 'Test User', 'test@example.com'))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    before = db.get_flight_by_id(flight_id)[10]
    booking_ref = db.create_booking(user_id, flight_id, 'Test Booker', 35)
    assert isinstance(booking_ref, str) and booking_ref.startswith('FLY')
    after = db.get_flight_by_id(flight_id)[10]
    assert after == before - 1, 'Available seats should decrement by 1'
    return user_id, booking_ref


def test_get_user_bookings_returns_created_booking(user_id, booking_ref):
    bookings = db.get_user_bookings(user_id)
    assert any(b[0] == booking_ref for b in bookings), 'Created booking should appear in user bookings'


def test_get_all_bookings_includes_user_booking():
    bookings = db.get_all_bookings()
    assert isinstance(bookings, list), 'Expected list of all bookings'
    return bookings


if __name__ == '__main__':
    setup_test_db()
    flight = test_search_flights_returns_available_flights()
    user_id, booking_ref = test_create_booking_reduces_seats_and_returns_ref(flight[0])
    test_get_user_bookings_returns_created_booking(user_id, booking_ref)
    all_bookings = test_get_all_bookings_includes_user_booking()
    print('All bookings count:', len(all_bookings))
    print('Booking flow tests passed.')
