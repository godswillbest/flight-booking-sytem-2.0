import streamlit as st
import database as db
from datetime import date

def search_flights():
    st.subheader("✈️ Find Your Flight")
    
    st.markdown("### Enter your travel details")
    
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox(
            "Departure City",
            ["Lagos (LOS)", "Abuja (ABV)", "Port Harcourt (PHC)", "Kano (KAN)", "Enugu (ENU)"],
            key="origin_select"
        )
    with col2:
        destination = st.selectbox(
            "Arrival City",
            ["Abuja (ABV)", "Lagos (LOS)", "Port Harcourt (PHC)", "Kano (KAN)", "Enugu (ENU)", 
             "Dubai (DXB)", "Nairobi (NBO)", "Addis Ababa (ADD)", "Doha (DOH)", "Kigali (KGL)", "Johannesburg (JNB)"],
            key="dest_select"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        travel_date = st.date_input("Travel Date", min_value=date.today(), key="travel_date")
    with col4:
        st.write("")
    
    search_clicked = st.button("🔍 Search Available Flights", use_container_width=True, key="search_flights_btn")
    
    if search_clicked:
        if origin == destination:
            st.error("❌ Origin and destination cannot be the same")
            return
        
        with st.spinner("Searching for flights..."):
            flights = db.search_available_flights(origin, destination, travel_date)
        
        if flights:
            st.success(f"🎉 {len(flights)} flights found from {origin} to {destination} on {travel_date}")
            
            for flight in flights:
                with st.container():
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"### ✈️ {flight[2]}")
                        st.markdown(f"**Flight Number:** `{flight[1]}`")
                        st.markdown(f"**Route:** {flight[3]} → {flight[4]}")
                    
                    with col2:
                        st.markdown(f"**Departure Date:** 📅 {flight[5]}")
                        st.markdown(f"**Departure Time:** ⏰ {flight[6]}")
                        st.markdown(f"**Arrival Time:** ⏰ {flight[7]}")
                        st.markdown(f"**Available Seats:** 💺 {flight[10]} / {flight[9]}")
                    
                    with col3:
                        st.markdown(f"### 💰 ₦{flight[8]:,.0f}")
                        if st.button(f"✈️ Book This Flight", key=f"book_flight_{flight[0]}"):
                            st.session_state['selected_flight_id'] = flight[0]
                            st.rerun()
        else:
            st.warning(f"❌ No flights available from {origin} to {destination} on {travel_date}. Please try different dates or cities.")


def booking_form():
    if 'selected_flight_id' not in st.session_state:
        st.rerun()
    
    flight = db.get_flight_by_id(st.session_state['selected_flight_id'])
    if not flight:
        st.error("Selected flight not found. Please search again.")
        if 'selected_flight_id' in st.session_state:
            del st.session_state['selected_flight_id']
        return
    
    st.subheader("📝 Complete Your Booking")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Airline:** {flight[2]}")
        st.markdown(f"**Flight Number:** {flight[1]}")
        st.markdown(f"**Route:** {flight[3]} → {flight[4]}")
    with col2:
        st.markdown(f"**Departure Date:** {flight[5]}")
        st.markdown(f"**Departure Time:** {flight[6]}")
        st.markdown(f"**Arrival Time:** {flight[7]}")
        st.markdown(f"**Price:** ₦{flight[8]:,.0f}")
    
    st.markdown("---")
    
    with st.form(key="booking_form"):
        st.markdown("### Passenger Information")
        
        passenger_name = st.text_input("Full Name (as on ID)", placeholder="Enter passenger's full name")
        passenger_age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("✅ Confirm Booking", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit_button:
            if not passenger_name:
                st.error("Please enter passenger name")
            else:
                try:
                    booking_ref = db.create_booking(
                        st.session_state['user_id'],
                        flight[0],
                        passenger_name.strip(),
                        passenger_age
                    )
                    st.success("✅ BOOKING CONFIRMED!")
                    st.success(f"📌 Booking Reference: {booking_ref}")
                    st.balloons()

                    if 'selected_flight_id' in st.session_state:
                        del st.session_state['selected_flight_id']
                    st.session_state['user_page'] = 'bookings'
                    st.rerun()
                except ValueError as ve:
                    st.error(str(ve))
                except Exception as e:
                    st.error("⚠️ Could not complete booking. Please try again.")
                    st.error(str(e))
        
        if cancel_button:
            if 'selected_flight_id' in st.session_state:
                del st.session_state['selected_flight_id']
            st.rerun()

def my_bookings():
    st.subheader("📋 My Booking History")
    st.markdown(f"**Logged in as:** {st.session_state.get('username', 'Unknown')} (User ID: {st.session_state.get('user_id', 'N/A')})")
    
    with st.spinner("Loading your bookings..."):
        bookings = db.get_user_bookings(st.session_state['user_id'])
    
    if bookings:
        st.success(f"You have {len(bookings)} booking(s)")
        
        for booking in bookings:
            with st.expander(f"📌 {booking[0]} - {booking[5]} ({booking[7]} → {booking[8]})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Passenger:** {booking[1]} (Age: {booking[2]})")
                    st.markdown(f"**Flight:** {booking[5]} - {booking[6]}")
                    st.markdown(f"**Route:** {booking[7]} → {booking[8]}")
                with col2:
                    st.markdown(f"**Departure:** {booking[9]} at {booking[10]}")
                    st.markdown(f"**Price:** ₦{booking[11]:,.0f}")
                    st.markdown(f"**Status:** {'✅ Confirmed' if booking[4] == 'confirmed' else '❌ Cancelled'}")
                st.markdown(f"**Booked on:** {booking[3]}")
    else:
        st.info("📭 You haven't made any bookings yet. Search for flights above to get started!")