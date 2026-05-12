import streamlit as st
import database as db
import random
import string
from datetime import datetime

def generate_booking_ref():
    return 'BK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def search_flights():
    st.subheader("✈️ Search Flights")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        origin = st.text_input("From (City)")
    with col2:
        destination = st.text_input("To (City)")
    with col3:
        date = st.date_input("Departure Date")
    
    if st.button("🔍 Search Flights", use_container_width=True):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM flights 
                         WHERE origin LIKE ? AND destination LIKE ? AND departure_date = ? 
                         AND available_seats > 0 ORDER BY price ASC""", 
                       (f'%{origin}%', f'%{destination}%', str(date)))
        flights = cursor.fetchall()
        conn.close()
        
        if flights:
            for flight in flights:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2,2,1,1])
                    with col1:
                        st.write(f"**{flight[2]}**")
                        st.write(f"🛫 {flight[3]} → 🛬 {flight[4]}")
                    with col2:
                        st.write(f"📅 {flight[5]}")
                        st.write(f"⏰ {flight[6]} - {flight[7]}")
                    with col3:
                        st.write(f"💰 KES {flight[8]:,.0f}")
                        st.write(f"💺 {flight[10]} seats left")
                    with col4:
                        if st.button("Book", key=f"book_{flight[0]}"):
                            st.session_state.selected_flight = flight
                            st.rerun()
                    st.divider()
        else:
            st.warning("No flights found. Try different dates or destinations.")

def booking_form():
    flight = st.session_state.selected_flight
    
    st.subheader(f"Booking: {flight[2]} - {flight[3]} to {flight[4]}")
    st.write(f"Date: {flight[5]} | Time: {flight[6]} | Price: KES {flight[8]:,.0f}")
    
    with st.form("booking_form"):
        passenger_name = st.text_input("Passenger Full Name")
        passenger_age = st.number_input("Passenger Age", min_value=1, max_value=120, step=1)
        
        if st.form_submit_button("Confirm Booking"):
            if passenger_name:
                conn = db.get_connection()
                cursor = conn.cursor()
                
                booking_ref = generate_booking_ref()
                booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("INSERT INTO bookings (booking_ref, user_id, flight_id, passenger_name, passenger_age, booking_date) VALUES (?, ?, ?, ?, ?, ?)",
                               (booking_ref, st.session_state.user_id, flight[0], passenger_name, passenger_age, booking_date))
                
                cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = ?", (flight[0],))
                conn.commit()
                conn.close()
                
                st.success(f"✅ Booking confirmed! Reference: {booking_ref}")
                del st.session_state.selected_flight
                st.rerun()
            else:
                st.error("Please enter passenger name")

def my_bookings():
    st.subheader("📋 My Bookings")
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT b.*, f.flight_number, f.airline, f.origin, f.destination, 
                      f.departure_date, f.departure_time, f.price 
                      FROM bookings b JOIN flights f ON b.flight_id = f.id 
                      WHERE b.user_id = ? ORDER BY b.booking_date DESC""", (st.session_state.user_id,))
    bookings = cursor.fetchall()
    conn.close()
    
    if bookings:
        for booking in bookings:
            with st.expander(f"📌 {booking[1]} - {booking[11]} ({booking[12]} to {booking[13]})"):
                st.write(f"**Passenger:** {booking[8]}")
                st.write(f"**Age:** {booking[9]}")
                st.write(f"**Flight:** {booking[11]} - {booking[10]}")
                st.write(f"**Date:** {booking[14]} at {booking[15]}")
                st.write(f"**Price:** KES {booking[16]:,.0f}")
                st.write(f"**Status:** {'✅ Confirmed' if booking[7] == 'confirmed' else '❌ Cancelled'}")
                
                if booking[7] == 'confirmed':
                    if st.button("Cancel Booking", key=f"cancel_{booking[0]}"):
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking[0],))
                        cursor.execute("UPDATE flights SET available_seats = available_seats + 1 WHERE id = ?", (booking[4],))
                        conn.commit()
                        conn.close()
                        st.success("Booking cancelled!")
                        st.rerun()
    else:
        st.info("You have no bookings yet.")