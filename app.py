import streamlit as st
import database as db
import auth
import user
import admin

# 1. Page Configuration
st.set_page_config(page_title="Flight Booking System", page_icon="✈️", layout="wide")

db.setup_database()

# 2. Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_page' not in st.session_state:
    st.session_state['user_page'] = 'search'

# 3. Sidebar
with st.sidebar:
    st.title("✈️ Menu")
    if st.session_state['logged_in']:
        st.write(f"👤 **{st.session_state.get('full_name')}**")
        if st.button("🚪 Logout", key="logout_btn"):
            auth.logout()
            st.rerun()

# 4. Main Router Logic
if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1: auth.show_login()
    with tab2: auth.show_register()

else:
    # --- ADMIN CHECK FIRST ---
    if st.session_state.get('role') == 'admin':
        admin.show_admin_dashboard()
    
    # --- USER LOGIC SECOND ---
    else:
        # If a flight is being booked, show the form and NOTHING else
        if 'selected_flight_id' in st.session_state:
            user.booking_form()
        
        # Otherwise, show standard navigation and pages
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Search Flights", use_container_width=True, key="nav_s"):
                    st.session_state['user_page'] = 'search'
                    st.rerun()
            with col2:
                if st.button("📋 My Bookings", use_container_width=True, key="nav_b"):
                    st.session_state['user_page'] = 'bookings'
                    st.rerun()
            
            st.markdown("---")
            
            if st.session_state['user_page'] == 'search':
                user.search_flights()
            else:
                user.my_bookings()