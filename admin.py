import streamlit as st
import pandas as pd
import database as db

DEFAULT_PROMOTIONS = [
    {'code': 'SKYFLOW10', 'discount': 10, 'description': '10% off selected routes', 'active': True},
    {'code': 'GOLD5', 'discount': 5, 'description': '5% off for frequent flyers', 'active': True}
]


def get_promotions():
    if 'promotions' not in st.session_state:
        st.session_state['promotions'] = DEFAULT_PROMOTIONS.copy()
    return st.session_state['promotions']


def show_admin_dashboard():
    st.title('Administrator Control Panel')
    st.markdown('Manage flights, bookings, users, and promotional campaigns from one dashboard.')

    tab1, tab2, tab3, tab4 = st.tabs(['📊 Manage Flights', '📋 Manage Bookings', '👥 Manage Users', '🎟 Manage Promotions'])

    with tab1:
        st.subheader('Flight Management')
        flights = db.get_all_flights()
        if flights:
            df = pd.DataFrame(flights, columns=['ID', 'Flight No', 'Airline', 'Origin', 'Destination', 'Date', 'Departure', 'Arrival', 'Price', 'Total Seats', 'Available Seats'])
            st.dataframe(df)
        else:
            st.info('No flights available yet.')

        with st.expander('Add New Flight'):
            with st.form('add_flight_form'):
                col1, col2 = st.columns(2)
                with col1:
                    flight_number = st.text_input('Flight Number', placeholder='NG1099')
                    airline = st.text_input('Airline', placeholder='SkyFlow Airways')
                    origin = st.text_input('Origin', placeholder='Lagos (LOS)')
                with col2:
                    destination = st.text_input('Destination', placeholder='Abuja (ABV)')
                    departure_date = st.date_input('Departure Date')
                    departure_time = st.text_input('Departure Time', placeholder='08:00')
                    arrival_time = st.text_input('Arrival Time', placeholder='10:00')
                price = st.number_input('Price', min_value=0, value=100000)
                total_seats = st.number_input('Total Seats', min_value=1, value=60)
                submit_flight = st.form_submit_button('Add Flight')
                if submit_flight:
                    if not flight_number or not airline or not origin or not destination:
                        st.error('Please complete all flight details.')
                    else:
                        try:
                            db.add_flight(
                                flight_number.strip().upper(),
                                airline.strip(),
                                origin.strip(),
                                destination.strip(),
                                departure_date.strftime('%Y-%m-%d'),
                                departure_time.strip(),
                                arrival_time.strip(),
                                float(price),
                                int(total_seats)
                            )
                            st.success(f'Flight {flight_number} added successfully.')
                            st.experimental_rerun()
                        except Exception as err:
                            st.error(f'Unable to add flight: {err}')

    with tab2:
        st.subheader('Bookings Overview')
        bookings = db.get_all_bookings()
        if bookings:
            df = pd.DataFrame(bookings, columns=[
                'Booking Ref', 'Passenger', 'Age', 'Date', 'Status', 'Flight No', 'Airline',
                'Origin', 'Destination', 'Depart Date', 'Depart Time', 'Fare', 'Trip Type',
                'Return Date', 'Adults', 'Children', 'Infants', 'Total Price', 'Payment Method',
                'Return Flight ID', 'Return Flight No', 'Return Origin', 'Return Destination',
                'Return Depart Date', 'Return Depart Time', 'Return Fare', 'Username', 'Full Name', 'Email'
            ])
            st.dataframe(df)
        else:
            st.info('No bookings have been made yet.')

    with tab3:
        st.subheader('User Accounts')
        users = db.get_all_users()
        if users:
            df = pd.DataFrame(users, columns=['ID', 'Username', 'Full Name', 'Email', 'Role'])
            st.dataframe(df)
        else:
            st.info('No registered users yet.')

        with st.expander('Add New Admin or User'):
            st.write('User creation is currently handled through registration. Use the database directly for bulk provisioning.')

    with tab4:
        st.subheader('Promotions Manager')
        promotions = get_promotions()
        for promo in promotions:
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{promo['code']}** — {promo['description']}")
            cols[1].markdown(f"**{promo['discount']}% Off**")
            cols[2].markdown('Active' if promo['active'] else 'Inactive')
            if cols[3].button(f"Toggle {promo['code']}", key=f"toggle_{promo['code']}"):
                promo['active'] = not promo['active']
                st.experimental_rerun()

        st.markdown('---')
        with st.form('new_promo_form'):
            promo_code = st.text_input('Promo Code')
            promo_discount = st.number_input('Discount (%)', min_value=1, max_value=100, value=10)
            promo_desc = st.text_input('Description', placeholder='Example: 10% off premium routes')
            promo_active = st.checkbox('Active', value=True)
            add_promo = st.form_submit_button('Add Promotion')
            if add_promo:
                if not promo_code or not promo_desc:
                    st.error('Please provide a valid promo code and description.')
                else:
                    promotions.append({
                        'code': promo_code.strip().upper(),
                        'discount': int(promo_discount),
                        'description': promo_desc.strip(),
                        'active': promo_active
                    })
                    st.success(f'Promotion {promo_code.strip().upper()} added.')
                    st.experimental_rerun()
