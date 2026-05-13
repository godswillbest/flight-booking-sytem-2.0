import streamlit as st
import database as db
from datetime import date

def search_flights():
    st.subheader("✈️ Find Your Flight")
    
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("Departure City", ["Lagos (LOS)", "Abuja (ABV)", "Port Harcourt (PHC)"], key="dep_city")
    with col2:
        dest = st.selectbox("Arrival City", ["Abuja (ABV)", "Lagos (LOS)", "Port Harcourt (PHC)", "Dubai (DXB)"], key="arr_city")
    
    t_date = st.date_input("Travel Date", min_value=date.today(), key="travel_dt")
    
    if st.button("🔍 Search Available Flights", use_container_width=True, key="do_search"):
        # Store results in session state so they don't disappear on rerun
        st.session_state['search_results'] = db.search_available_flights(origin, dest, t_date)
        if not st.session_state['search_results']:
            st.warning("No flights found for this route.")

    # Display results if they exist in session state
    if 'search_results' in st.session_state and st.session_state['search_results']:
        for f in st.session_state['search_results']:
            with st.container():
                st.markdown("---")
                st.write(f"### {f[2]} ({f[1]})")
                st.write(f"Price: ₦{f[8]:,.0f} | Seats: {f[10]}")
                if st.button(f"Book {f[1]}", key=f"book_btn_{f[0]}"):
                    st.session_state['selected_flight_id'] = f[0]
                    # Clear search results so we don't see them behind the booking form
                    del st.session_state['search_results']
                    st.rerun()

def booking_form():
    flight_id = st.session_state.get('selected_flight_id')
    flight = db.get_flight_by_id(flight_id)
    
    if not flight:
        st.error("Error: Flight details not found.")
        if st.button("Return to Search"):
            if 'selected_flight_id' in st.session_state: del st.session_state['selected_flight_id']
            st.rerun()
        return

    st.subheader("📝 Complete Your Passenger Details")
    st.info(f"Booking Flight: {flight[2]} ({flight[1]}) | {flight[3]} to {flight[4]}")
    
    with st.form("final_booking_form"):
        p_name = st.text_input("Passenger Name", value=st.session_state.get('full_name', ''))
        p_age = st.number_input("Passenger Age", min_value=1, value=25)
        
        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("✅ Finalize Booking")
        cancel = col2.form_submit_button("❌ Cancel")
        
        if submit:
            try:
                # Save booking to database
                ref = db.create_booking(st.session_state['user_id'], flight[0], p_name, p_age)
                st.success(f"Booking Confirmed! Your reference is: {ref}")
                st.balloons()
                # Clean up state and redirect to history
                del st.session_state['selected_flight_id']
                st.session_state['user_page'] = 'bookings'
                st.rerun()
            except Exception as e:
                st.error(f"Database Error: {e}")
        
        if cancel:
            del st.session_state['selected_flight_id']
            st.rerun()

def my_bookings():
    st.subheader("📋 My Booking History")
    bookings = db.get_user_bookings(st.session_state['user_id'])
    if bookings:
        for b in bookings:
            st.info(f"Ref: {b[0]} | Flight: {b[5]} | Date: {b[9]} | Status: {b[4]}")
    else:
        st.write("You have no booking history.")