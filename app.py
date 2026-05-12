import streamlit as st
import database as db
import auth
import user
import admin

# Page configuration
st.set_page_config(
    page_title="Flight Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db.setup_database()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_page' not in st.session_state:
    st.session_state['user_page'] = 'search'

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933244.png", width=60)
    st.title("✈️ Flight Booking")
    st.markdown("---")
    
    if st.session_state['logged_in']:
        st.write(f"👤 **{st.session_state.get('full_name', 'User')}**")
        st.write(f"📧 {st.session_state.get('user_email', '')}")
        st.write(f"👑 Role: **{st.session_state.get('role', 'user').upper()}**")
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            auth.logout()
    else:
        st.info("Please login or register to continue")

# Main content
if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        auth.show_login()
    with tab2:
        auth.show_register()
else:
    if st.session_state['role'] == 'admin':
        admin.show_admin_dashboard()
    else:
        if 'selected_flight_id' in st.session_state:
            user.booking_form()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Search Flights", use_container_width=True, key="nav_search"):
                    st.session_state['user_page'] = 'search'
                    st.rerun()
            with col2:
                if st.button("📋 My Bookings", use_container_width=True, key="nav_bookings"):
                    st.session_state['user_page'] = 'bookings'
                    st.rerun()
            
            st.markdown("---")
            
            if st.session_state['user_page'] == 'search':
                user.search_flights()
            else:
                user.my_bookings()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>© 2026 Flight Booking System | CSC 206 Web Design and Development</p>",
    unsafe_allow_html=True
)