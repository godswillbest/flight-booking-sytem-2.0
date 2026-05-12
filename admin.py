import streamlit as st
import database as db

def admin_dashboard():
    st.subheader("🛠️ Admin Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Flight", "📊 All Flights", "👥 All Bookings", "👤 All Users"])
    
    with tab1:
        with st.form("add_flight"):
            st.write("### Add New Flight")
            col1, col2 = st.columns(2)
            with col1:
                flight_number = st.text_input("Flight Number")
                airline = st.text_input("Airline")
                origin = st.text_input("Origin")
                destination = st.text_input("Destination")
            with col2:
                departure_date = st.date_input("Departure Date")
                departure_time = st.text_input("Departure Time (HH:MM)")
                arrival_time = st.text_input("Arrival Time (HH:MM)")
                price = st.number_input("Price (KES)", min_value=0)
                total_seats = st.number_input("Total Seats", min_value=1)
            
            if st.form_submit_button("Add Flight"):
                conn = db.get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""INSERT INTO flights (flight_number, airline, origin, destination, 
                                      departure_date, departure_time, arrival_time, price, total_seats, available_seats) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                   (flight_number, airline, origin, destination, str(departure_date), 
                                    departure_time, arrival_time, price, total_seats, total_seats))
                    conn.commit()
                    st.success("Flight added successfully!")
                except:
                    st.error("Flight number already exists")
                finally:
                    conn.close()
    
    with tab2:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flights ORDER BY departure_date")
        flights = cursor.fetchall()
        conn.close()
        
        for flight in flights:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{flight[1]}** - {flight[2]} | {flight[3]} → {flight[4]} | {flight[5]} | KES {flight[8]:,.0f} | Seats: {flight[10]}/{flight[9]}")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{flight[0]}"):
                    st.session_state.edit_flight = flight
            with col3:
                if st.button("🗑️ Delete", key=f"del_{flight[0]}"):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM flights WHERE id = ?", (flight[0],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            st.divider()
    
    with tab3:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT b.booking_ref, b.passenger_name, b.booking_date, b.status,
                          f.flight_number, f.origin, f.destination, f.departure_date, u.username
                          FROM bookings b 
                          JOIN flights f ON b.flight_id = f.id 
                          JOIN users u ON b.user_id = u.id
                          ORDER BY b.booking_date DESC""")
        bookings = cursor.fetchall()
        conn.close()
        
        for booking in bookings:
            st.write(f"📌 {booking[0]} - {booking[4]} | {booking[1]} | {booking[8]} | Status: {booking[3]}")
    
    with tab4:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role FROM users")
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            st.write(f"👤 {user[1]} - {user[2]} ({user[4]}) | {user[3]}")