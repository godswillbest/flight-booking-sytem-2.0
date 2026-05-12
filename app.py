import streamlit as st
import database as db
import auth
import user
import admin

# Page configuration
st.set_page_config(
    page_title="Flight Booking System",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Run database setup (only once)
db.setup_database()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933244.png", width=80)
    st.title("✈️ Flight Booking")
    
    if st.session_state.logged_in:
        st.write(f"Welcome, **{st.session_state.full_name}**")
        st.write(f"Role: {st.session_state.role}")
        
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
    else:
        st.write("Please login or register")

# Main content
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        auth.login()
    with tab2:
        auth.register()
else:
    st.title("✈️ Flight Booking System")
    
    if st.session_state.role == 'admin':
        admin.admin_dashboard()
    else:
        menu = st.radio("Menu", ["🔍 Search Flights", "📋 My Bookings"], horizontal=True)
        
        if menu == "🔍 Search Flights":
            if 'selected_flight' in st.session_state:
                user.booking_form()
            else:
                user.search_flights()
        else:
            user.my_bookings()

# Footer
st.markdown("---")
st.markdown("© 2025 Flight Booking System | CSC 206 Project")