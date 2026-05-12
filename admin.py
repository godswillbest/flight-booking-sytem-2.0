import streamlit as st
import pandas as pd
import database as db

def show_admin_dashboard():
    st.subheader("🛠️ Administrator Control Panel")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Manage Flights", "➕ Add New User", "👥 All Users", "📋 All Bookings"])
    
    # TAB 1: Manage Flights
    with tab1:
        st.markdown("### Add New Flight")
        
        with st.form("add_flight_form"):
            col1, col2 = st.columns(2)
            with col1:
                flight_number = st.text_input("Flight Number", placeholder="e.g., NG1099", key="admin_flight_no")
                airline = st.text_input("Airline", placeholder="e.g., Nigeria Air", key="admin_airline")
                origin = st.text_input("Origin", placeholder="e.g., Lagos (LOS)", key="admin_origin")
                destination = st.text_input("Destination", placeholder="e.g., Abuja (ABV)", key="admin_dest")
            with col2:
                departure_date = st.date_input("Departure Date", key="admin_date")
                departure_time = st.text_input("Departure Time", placeholder="08:00", key="admin_dep_time")
                arrival_time = st.text_input("Arrival Time", placeholder="09:30", key="admin_arr_time")
                price = st.number_input("Price (₦)", min_value=0, step=1000, key="admin_price")
                total_seats = st.number_input("Total Seats", min_value=1, step=1, key="admin_seats")
            
            submitted = st.form_submit_button("✈️ Add Flight", use_container_width=True)
            
            if submitted:
                if all([flight_number, airline, origin, destination, departure_time, arrival_time]):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            INSERT INTO flights (flight_number, airline, origin, destination, 
                                               departure_date, departure_time, arrival_time, 
                                               price, total_seats, available_seats)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (flight_number, airline, origin, destination, str(departure_date),
                              departure_time, arrival_time, price, total_seats, total_seats))
                        conn.commit()
                        st.success(f"✅ Flight {flight_number} added successfully!")
                    except Exception as e:
                        st.error(f"Flight number already exists: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("Please fill all fields")
        
        st.markdown("---")
        st.markdown("### Existing Flights")
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flights ORDER BY departure_date")
        flights = cursor.fetchall()
        conn.close()
        
        if flights:
            for flight in flights:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{flight[1]}** - {flight[2]} | {flight[3]} → {flight[4]} | {flight[5]} | ₦{flight[8]:,.0f} | Seats: {flight[10]}/{flight[9]}")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{flight[0]}"):
                        st.info("Edit feature coming soon")
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{flight[0]}"):
                        conn2 = db.get_connection()
                        cursor2 = conn2.cursor()
                        cursor2.execute("DELETE FROM flights WHERE id = ?", (flight[0],))
                        conn2.commit()
                        conn2.close()
                        st.rerun()
        else:
            st.info("No flights found")
    
    # TAB 2: Add User
    with tab2:
        with st.form("admin_add_user_form"):
            username = st.text_input("Username", key="admin_username")
            full_name = st.text_input("Full Name", key="admin_fullname")
            email = st.text_input("Email", key="admin_email")
            password = st.text_input("Password", type="password", key="admin_password")
            role = st.selectbox("Role", ["user", "admin"], key="admin_role")
            
            if st.form_submit_button("➕ Add User", use_container_width=True):
                if username and password:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    hashed = db.hash_password(password)
                    try:
                        cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                                      (username, hashed, full_name, email, role))
                        conn.commit()
                        st.success(f"✅ User {username} added successfully!")
                    except:
                        st.error("Username already exists")
                    finally:
                        conn.close()
                else:
                    st.error("Username and password required")
    
    # TAB 3: All Users
    with tab3:
        st.markdown("### Registered Users")
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "ID": user[0],
                    "Username": user[1],
                    "Full Name": user[2],
                    "Email": user[3],
                    "Role": "👑 Admin" if user[4] == "admin" else "👤 User"
                })
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.info(f"📊 Total Users: {len(users)}")
        else:
            st.info("No users found")
    
    # TAB 4: All Bookings
    with tab4:
        st.markdown("### All Customer Bookings")
        
        bookings = db.get_all_bookings()
        
        if bookings:
            st.success(f"📊 Total Bookings in System: {len(bookings)}")
            
            # Summary statistics
            confirmed = sum(1 for b in bookings if b[4] == 'confirmed')
            cancelled = len(bookings) - confirmed
            st.info(f"✅ Confirmed: {confirmed} | ❌ Cancelled: {cancelled}")
            
            st.markdown("---")
            
            for booking in bookings:
                with st.expander(f"📌 {booking[0]} - {booking[5]} ({booking[7]} → {booking[8]})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Passenger:** {booking[1]} (Age: {booking[2]})")
                        st.markdown(f"**Flight:** {booking[5]} - {booking[6]}")
                        st.markdown(f"**Route:** {booking[7]} → {booking[8]}")
                        st.markdown(f"**Departure:** {booking[9]} at {booking[10]}")
                    with col2:
                        st.markdown(f"**Price:** ₦{booking[11]:,.0f}")
                        st.markdown(f"**Status:** {'✅ Confirmed' if booking[4] == 'confirmed' else '❌ Cancelled'}")
                        st.markdown(f"**Booked By:** {booking[12]} ({booking[14]})")
                        st.markdown(f"**Booking Date:** {booking[3]}")
        else:
            st.error("⚠️ NO BOOKINGS IN DATABASE")
            st.info("Users need to book flights before bookings appear here")