import streamlit as st
import database as db
import auth
import user
import admin

st.set_page_config(
    page_title="SkyFlow Airlines",
    page_icon="✈️",
    layout="wide"
)


def load_custom_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()
db.setup_database()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'
if 'booking_stage' not in st.session_state:
    st.session_state['booking_stage'] = None
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'
if 'currency' not in st.session_state:
    st.session_state['currency'] = 'NGN'
if 'notifications' not in st.session_state:
    st.session_state['notifications'] = [
        'Welcome aboard! Book your next trip with ease.',
        'Try the new track flight tool for live status updates.',
        'Use SKYFLOW10 for a 10% discount on selected routes.'
    ]

with st.sidebar:
    st.markdown('<div class="brand-logo">✈ SkyFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tag">AIRLINES</div>', unsafe_allow_html=True)
    st.markdown('---')

    if st.session_state['logged_in']:
        st.markdown(
            f'<div class="user-card">'
            f'<div class="user-avatar">{st.session_state.get("full_name", "?")[0]}</div>'
            f'<div><div class="user-name">{st.session_state.get("full_name")}</div>'
            f'<div class="user-role">{st.session_state.get("role", "User").title()} Member</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown('---')

        if st.session_state.get('role') == 'admin':
            menu_items = []
        else:
            menu_items = [
                'Home', 'Search Flights', 'Flight Schedule', 'My Bookings',
                'Payment History', 'Flight Status', 'Customer Support', 'Notifications',
                'Profile'
            ]

        if menu_items:
            choice = st.radio('Navigation', menu_items, index=menu_items.index(st.session_state['page']) if st.session_state['page'] in menu_items else 0)
            st.session_state['page'] = choice
        else:
            st.markdown("**Admin Dashboard**")
        st.markdown('---')
        st.selectbox('Language', ['English', 'French'], key='language')
        st.selectbox('Currency', ['NGN', 'USD', 'EUR'], key='currency')
        st.markdown('---')
        if st.button('🚪 Sign out'):
            auth.logout()
    else:
        st.markdown('Welcome to SkyFlow Airlines. Please log in to search flights, manage bookings, and track travel.')

if not st.session_state['logged_in']:
    tab1, tab2 = st.tabs(['🔐 Login', '📝 Register'])
    with tab1:
        auth.show_login()
    with tab2:
        auth.show_register()
else:
    if st.session_state.get('role') == 'admin':
        admin.show_admin_dashboard()
    else:
        if st.session_state['booking_stage'] == 'booking':
            user.booking_form()
        elif st.session_state['booking_stage'] == 'confirmation':
            user.confirmation_page()
        else:
            page = st.session_state['page']
            if page == 'Home':
                user.dashboard_home()
            elif page == 'Search Flights':
                user.search_flights()
            elif page == 'Flight Schedule':
                user.schedule_page()
            elif page == 'Track Flight':
                user.track_flight()
            elif page == 'My Bookings':
                user.my_bookings()
            elif page == 'Payment History':
                user.payment_history()
            elif page == 'Flight Status':
                user.track_flight()
            elif page == 'Customer Support':
                user.support_page()
            elif page == 'Notifications':
                user.notifications_page()
            elif page == 'Profile':
                user.user_profile()
            else:
                user.dashboard_home()
