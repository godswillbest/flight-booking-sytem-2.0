import streamlit as st
import database as db
from datetime import date, datetime
from io import BytesIO
import re

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

try:
    import qrcode
    from PIL import Image
except ImportError:
    qrcode = None
    Image = None

LOCATIONS = [
    "Lagos (LOS)", "Abuja (ABV)", "Port Harcourt (PHC)", "Kano (KAN)", "Enugu (ENU)",
    "Ibadan (IBA)", "Benin City (BNI)", "Owerri (QOW)", "Kaduna (KAD)", "Jos (JOS)",
    "Yola (YOL)", "Uyo (QUO)", "Maiduguri (MIU)", "Sokoto (SKO)", "Yenagoa (YEO)",
    "Calabar (CBQ)", "Akure (AKR)", "Ilorin (ILR)", "Zaria (ZAR)", "Asaba (ABB)",
    "Makurdi (MDI)", "Gombe (GMO)", "Dubai (DXB)", "Doha (DOH)", "Nairobi (NBO)",
    "Addis Ababa (ADD)", "Kigali (KGL)", "Johannesburg (JNB)", "Cairo (CAI)",
    "Accra (ACC)", "Dakar (DSS)", "Cape Town (CPT)", "London (LHR)", "Paris (CDG)",
    "Frankfurt (FRA)", "Amsterdam (AMS)", "New York (JFK)", "Toronto (YYZ)", "Los Angeles (LAX)",
    "Mumbai (BOM)", "Sydney (SYD)", "Singapore (SIN)", "Tokyo (NRT)", "Hong Kong (HKG)",
    "Bangkok (BKK)", "Rome (FCO)", "Barcelona (BCN)", "Istanbul (IST)", "Madrid (MAD)",
    "Dublin (DUB)", "Kuala Lumpur (KUL)", "Jakarta (CGK)", "Auckland (AKL)", "Melbourne (MEL)"
]

SEAT_LAYOUT = [
    ("A", "Window"), ("B", "Middle"), ("C", "Aisle"),
    ("D", "Aisle"), ("E", "Middle"), ("F", "Window")
]

PROMO_CODES = {
    "SKYFLOW10": 0.10,
    "GOLD5": 0.05,
    "TRAVEL20": 0.20
}


def format_currency(amount, currency='NGN'):
    try:
        rate = db.CURRENCY_RATES.get(currency, 1.0)
        converted = amount * rate
    except Exception:
        converted = amount
    symbol = {'NGN': '₦', 'USD': '$', 'EUR': '€'}.get(currency, '₦')
    precision = 2 if currency != 'NGN' else 0
    return f"{symbol}{converted:,.{precision}f}"


def get_location_suggestions(query, exclude=None):
    exclude = exclude or []
    query = query.strip().lower()
    candidates = [loc for loc in LOCATIONS if loc not in exclude]
    if not query:
        return candidates[:20]
    return [loc for loc in candidates if query in loc.lower()][:20]


def build_seat_options(flight_id):
    seat_items = []
    for row in range(1, 8):
        for col, seat_type in SEAT_LAYOUT:
            seat_label = f"{row}{col}"
            seat_items.append((seat_label, seat_type))
    occupied = [seat for seat, _ in seat_items if hash(f"{flight_id}-{seat}") % 7 == 0]
    options = [seat for seat, _ in seat_items if seat not in occupied]
    return seat_items, set(occupied), options


def draw_seat_map(flight_id, selected_seat=None):
    seat_items, occupied, _ = build_seat_options(flight_id)
    rows = []
    for row in range(1, 8):
        row_html = []
        for col, seat_type in SEAT_LAYOUT:
            seat_label = f"{row}{col}"
            if seat_label == selected_seat:
                color = '#1d4ed8'
                text = f"{seat_label} ✓"
            elif seat_label in occupied:
                color = '#ef4444'
                text = seat_label
            elif seat_type == 'Window':
                color = '#38bdf8'
                text = seat_label
            elif seat_type == 'Aisle':
                color = '#fbbf24'
                text = seat_label
            else:
                color = '#94a3b8'
                text = seat_label
            row_html.append(
                f"<div style='margin:2px;padding:10px 12px;background:{color};border-radius:12px;color:#fff;display:inline-block;font-size:12px;min-width:45px;text-align:center;'>{text}</div>"
            )
        rows.append(''.join(row_html))
    st.markdown(
        '<div style="display:flex;flex-direction:column;gap:6px;">' +
        ''.join(f"<div>{row}</div>" for row in rows) +
        '</div>',
        unsafe_allow_html=True
    )
    st.caption('Window seats are blue, aisle seats are amber, occupied seats are red.')


def generate_ticket_pdf(details):
    if FPDF is None:
        return None
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, 'SkyFlow Airlines Passenger Ticket', ln=True, align='C')
    pdf.ln(6)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, f"Booking Reference: {details['booking_ref']}", ln=True)
    pdf.cell(0, 6, f"Passenger: {details['passenger_name']}", ln=True)
    pdf.cell(0, 6, f"Flight: {details['airline']} {details['flight_number']}", ln=True)
    pdf.cell(0, 6, f"Route: {details['origin']} → {details['destination']}", ln=True)
    pdf.cell(0, 6, f"Departure: {details['departure_date']} {details['departure_time']}", ln=True)
    pdf.cell(0, 6, f"Seat: {details['seat_number']}", ln=True)
    pdf.cell(0, 6, f"Price: {details['price_text']}", ln=True)
    pdf.ln(6)
    pdf.multi_cell(0, 6, 'Thank you for choosing SkyFlow Airlines. Safe travels!')
    return pdf.output(dest='S').encode('latin-1')


def send_booking_confirmation_email(address, booking_ref):
    return f"A confirmation email has been sent to {address}. Your booking reference is {booking_ref}."


def dashboard_home():
    st.title('Welcome to SkyFlow')
    st.markdown('Experience modern flight booking, live tracking, and schedule planning with SkyFlow Airlines.')
    flights = db.get_all_flights()
    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Destinations', len(LOCATIONS))
    with col2:
        st.metric('Scheduled Flights', len(flights))
    with col3:
        st.metric('Active Notifications', len(st.session_state.get('notifications', [])))

    if st.session_state.get('notifications'):
        with st.expander('Latest Notifications'):
            for note in st.session_state['notifications']:
                st.write(f'• {note}')

    if st.session_state.get('favorite_routes'):
        st.markdown('### Favorite Routes')
        for route in st.session_state['favorite_routes']:
            st.write(f'⭐ {route}')


def search_flights():
    st.markdown('Search available flights using the filters below.')
    currency = st.session_state.get('currency', 'NGN')

    col1, col2 = st.columns(2)
    with col1:
        origin_query = st.text_input('Departure city or airport', value=st.session_state.get('origin_query', ''), key='origin_query')
        origin_options = get_location_suggestions(origin_query)
        origin = st.selectbox('Departure City', origin_options, key='origin_select')
    with col2:
        destination_query = st.text_input('Arrival city or airport', value=st.session_state.get('destination_query', ''), key='destination_query')
        destination_options = get_location_suggestions(destination_query, exclude=[origin])
        destination = st.selectbox('Arrival City', destination_options, key='destination_select')

    trip_type = st.radio('Trip Type', ['One-way', 'Round trip'], horizontal=True, key='trip_type')
    today = date.today()
    col3, col4 = st.columns(2)
    with col3:
        departure_date = st.date_input('Departure Date', min_value=today, value=st.session_state.get('departure_date', today), key='departure_date')
    with col4:
        return_date = None
        if trip_type == 'Round trip':
            return_date = st.date_input('Return Date', min_value=departure_date, value=st.session_state.get('return_date', departure_date), key='return_date')

    col5, col6, col7 = st.columns(3)
    with col5:
        adults = st.number_input('Adults (12+ yrs)', min_value=1, value=st.session_state.get('adults', 1), key='adults')
    with col6:
        children = st.number_input('Children (2-11 yrs)', min_value=0, value=st.session_state.get('children', 0), key='children')
    with col7:
        infants = st.number_input('Infants (0-24 months)', min_value=0, value=st.session_state.get('infants', 0), key='infants')

    seats_required = adults + children + infants
    st.markdown(f'**Passengers:** {adults} adult(s), {children} child(ren), {infants} infant(s)')

    st.markdown('---')
    col8, col9, col10 = st.columns(3)
    with col8:
        available_airlines = ['Any'] + db.get_distinct_airlines()
        airline_filter = st.selectbox('Airline', available_airlines, key='filter_airline')
    with col9:
        seat_class_filter = st.selectbox('Seat Class', ['Any', 'Economy', 'Business'], key='filter_seat_class')
    with col10:
        stops_filter = st.selectbox('Stops', ['Any', 'Direct', '1 Stop'], key='filter_stops')

    min_price, max_price = st.slider('Price Range', 0, 1000000, (0, 600000), step=10000, key='price_range')

    if st.button('Search Flights', use_container_width=True, key='search_button'):
        if origin == destination:
            st.warning('Departure and arrival cities cannot be the same.')
            return
        if trip_type == 'Round trip' and return_date is None:
            st.warning('Please select a return date for a round trip.')
            return

        st.session_state['booking_details'] = {
            'origin': origin,
            'destination': destination,
            'trip_type': trip_type,
            'departure_date': str(departure_date),
            'return_date': str(return_date) if return_date else None,
            'adults': adults,
            'children': children,
            'infants': infants,
            'filter_airline': airline_filter,
            'filter_seat_class': seat_class_filter,
            'filter_stops': stops_filter,
            'price_range': [min_price, max_price],
            'currency': currency
        }
        recent = st.session_state.get('recent_searches', [])
        recent.insert(0, f"{origin} → {destination} on {departure_date}")
        st.session_state['recent_searches'] = recent[:8]

        search_kwargs = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'seats_required': seats_required,
            'min_price': min_price,
            'max_price': max_price,
            'airline': None if airline_filter == 'Any' else airline_filter,
            'seat_class': None if seat_class_filter == 'Any' else seat_class_filter,
            'stops': None if stops_filter == 'Any' else stops_filter
        }

        if trip_type == 'One-way':
            st.session_state['search_results'] = db.search_available_flights(**search_kwargs)
            st.session_state.pop('outbound_results', None)
            st.session_state.pop('return_results', None)
            st.session_state.pop('selected_outbound_id', None)
            st.session_state.pop('selected_return_id', None)
        else:
            outbound = db.search_available_flights(**search_kwargs)
            search_kwargs['origin'], search_kwargs['destination'] = destination, origin
            return_flights = db.search_available_flights(**search_kwargs)
            st.session_state['outbound_results'] = outbound
            st.session_state['return_results'] = return_flights
            st.session_state.pop('search_results', None)

    if st.session_state.get('trip_type') == 'One-way':
        if 'search_results' in st.session_state:
            if st.session_state['search_results']:
                for f in st.session_state['search_results']:
                    with st.container():
                        st.markdown('---')
                        st.markdown(f"### {f[2]} — {f[3]} → {f[4]}")
                        st.write(f"**Departure:** {f[5]} | **Arrival:** {f[7]}")
                        st.write(f"**Class:** Economy | **Seats left:** {f[10]}")
                        st.write(f"**Price per seat:** {format_currency(f[8], currency)}")
                        total_cost = f[8] * seats_required
                        st.write(f"**Total cost:** {format_currency(total_cost, currency)}")
                        if st.button(f"Book {f[1]}", key=f"book_btn_{f[0]}"):
                            st.session_state['selected_flight_id'] = f[0]
                            st.session_state['selected_return_flight_id'] = None
                            st.session_state['booking_stage'] = 'booking'
                            st.rerun()
            else:
                st.info('No available flights were found for this route. Please adjust your filters or choose another date.')

    if st.session_state['trip_type'] == 'Round trip':
        st.markdown('### Outbound Flights')
        if st.session_state.get('outbound_results'):
            for f in st.session_state['outbound_results']:
                with st.container():
                    st.markdown('---')
                    st.write(f"**{f[1]}** | {f[3]} → {f[4]} | {f[5]} - {f[7]}")
                    st.write(f"{format_currency(f[8], currency)} per seat | {f[10]} left")
                    if st.button('Select outbound', key=f"outbound_btn_{f[0]}"):
                        st.session_state['selected_outbound_id'] = f[0]
                        st.rerun()
        else:
            st.info('Search for outbound flights.')

        st.markdown('### Return Flights')
        if st.session_state.get('return_results'):
            for f in st.session_state['return_results']:
                with st.container():
                    st.markdown('---')
                    st.write(f"**{f[1]}** | {f[3]} → {f[4]} | {f[5]} - {f[7]}")
                    st.write(f"{format_currency(f[8], currency)} per seat | {f[10]} left")
                    if st.button('Select return', key=f"return_btn_{f[0]}"):
                        st.session_state['selected_return_id'] = f[0]
                        st.rerun()
        else:
            st.info('Search for return flights.')

        outbound_id = st.session_state.get('selected_outbound_id')
        return_id = st.session_state.get('selected_return_id')
        if outbound_id or return_id:
            st.markdown('---')
            st.markdown('### Selected Round Trip Flights')
            if outbound_id:
                outbound = db.get_flight_by_id(outbound_id)
                st.write(f"Outbound: {outbound[2]} ({outbound[1]}) — {outbound[3]} → {outbound[4]} at {outbound[5]}")
            if return_id:
                rtn = db.get_flight_by_id(return_id)
                st.write(f"Return: {rtn[2]} ({rtn[1]}) — {rtn[3]} → {rtn[4]} at {rtn[5]}")

        if outbound_id and return_id:
            if st.button('▶ Proceed to passenger details', key='proceed_roundtrip'):
                st.session_state['selected_flight_id'] = outbound_id
                st.session_state['selected_return_flight_id'] = return_id
                st.session_state['booking_stage'] = 'booking'
                st.rerun()


def booking_form():
    flight_id = st.session_state.get('selected_flight_id')
    return_flight_id = st.session_state.get('selected_return_flight_id')
    flight = db.get_flight_by_id(flight_id)
    return_flight = db.get_flight_by_id(return_flight_id) if return_flight_id else None
    booking_details = st.session_state.get('booking_details', {})

    if not flight:
        st.error('Flight details not found.')
        if st.button('Return to Search'):
            for key in ['selected_flight_id', 'selected_return_flight_id', 'booking_details', 'selected_outbound_id', 'selected_return_id', 'booking_stage']:
                st.session_state.pop(key, None)
            st.rerun()
        return

    total_passengers = booking_details.get('adults', 1) + booking_details.get('children', 0) + booking_details.get('infants', 0)
    total_price = flight[8] * total_passengers
    if return_flight:
        total_price += return_flight[8] * total_passengers

    st.subheader('Passenger & Payment Details')
    st.info(f"Booking: {flight[2]} ({flight[1]}) from {flight[3]} to {flight[4]}")
    st.markdown(f"**Trip type:** {booking_details.get('trip_type')} | **Passengers:** {total_passengers}")
    if return_flight:
        st.markdown(f"**Return route:** {return_flight[3]} → {return_flight[4]} at {return_flight[5]}")

    promo_code = st.text_input('Promo Code', value=st.session_state.get('promo_code', ''), key='promo_code')
    seat_preference = st.selectbox('Seat Preference', ['Window Seat', 'Middle Seat', 'Aisle Seat'], key='seat_preference')
    seat_items, occupied, seat_choices = build_seat_options(flight[0])
    selected_seat = st.selectbox('Preferred Seat Number', seat_choices, key='seat_number')
    draw_seat_map(flight[0], selected_seat)

    seat_fee = db.WINDOW_SEAT_FEE if seat_preference == 'Window Seat' else 0
    discount_rate = PROMO_CODES.get(promo_code.strip().upper(), 0)
    discount_amount = (total_price + seat_fee * total_passengers) * discount_rate
    net_total = total_price + seat_fee * total_passengers - discount_amount

    st.markdown('---')
    st.markdown(f"**Fare total:** {format_currency(total_price, booking_details.get('currency', 'NGN'))}")
    st.markdown(f"**Seat fee:** {format_currency(seat_fee * total_passengers, booking_details.get('currency', 'NGN'))}")
    st.markdown(f"**Discount:** {format_currency(discount_amount, booking_details.get('currency', 'NGN'))}")
    st.markdown(f"**Total payable:** {format_currency(net_total, booking_details.get('currency', 'NGN'))}")

    with st.form('complete_booking_form'):
        full_name = st.text_input('Full Name', key='full_name', value=st.session_state.get('full_name', ''))
        email = st.text_input('Email Address', key='passenger_email', value=st.session_state.get('user_email', ''))
        phone = st.text_input('Phone Number', key='passenger_phone', value=st.session_state.get('user_phone', ''))
        age = st.number_input('Age', min_value=0, value=st.session_state.get('lead_age', 30), key='lead_age')
        nationality = st.text_input('Nationality', key='nationality', value=st.session_state.get('nationality', 'Nigeria'))
        payment_method = st.selectbox('Payment Method', ['Credit / Debit Card', 'Mobile Money', 'Bank Transfer'], key='payment_method')
        payment_reference = st.text_input('Payment Reference', placeholder='Transaction ID or account number', key='payment_reference')
        submit_button = st.form_submit_button('Complete Booking')
        cancel_button = st.form_submit_button('Cancel Booking')

    if submit_button:
        if not full_name.strip() or not email.strip() or not phone.strip() or not nationality.strip():
            st.error('Please complete all required passenger details.')
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error('Please enter a valid email address.')
            return
        if not phone.replace('+', '').replace(' ', '').isdigit():
            st.error('Please enter a valid phone number.')
            return

        try:
            booking_ref = db.create_booking(
                st.session_state['user_id'],
                flight[0],
                full_name,
                age,
                booking_details.get('trip_type', 'One-way'),
                booking_details.get('return_date'),
                booking_details.get('adults', 1),
                booking_details.get('children', 0),
                booking_details.get('infants', 0),
                payment_method,
                net_total,
                return_flight[0] if return_flight else None
            )

            st.session_state['confirmation_data'] = {
                'booking_ref': booking_ref,
                'passenger_name': full_name,
                'email': email,
                'phone': phone,
                'airline': flight[2],
                'flight_number': flight[1],
                'origin': flight[3],
                'destination': flight[4],
                'departure_date': flight[5],
                'departure_time': flight[6],
                'arrival_time': flight[7],
                'seat_number': selected_seat,
                'seat_preference': seat_preference,
                'price_text': format_currency(net_total, booking_details.get('currency', 'NGN')),
                'total_price': net_total,
                'currency': booking_details.get('currency', 'NGN'),
                'payment_method': payment_method,
                'booking_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.success(f'Booking complete. Reference: {booking_ref}')
            st.success(send_booking_confirmation_email(email, booking_ref))
            st.session_state['booking_stage'] = 'confirmation'
            st.rerun()
        except Exception as err:
            st.error(f'Booking failed: {err}')

    if cancel_button:
        for key in ['selected_flight_id', 'selected_return_flight_id', 'booking_details', 'selected_outbound_id', 'selected_return_id', 'booking_stage']:
            st.session_state.pop(key, None)
        st.rerun()


def confirmation_page():
    data = st.session_state.get('confirmation_data')
    if not data:
        st.error('No booking confirmation available.')
        return

    st.success('🎉 Booking Confirmed!')
    st.markdown(f"**Booking Reference:** {data['booking_ref']}")
    st.markdown(f"**Passenger:** {data['passenger_name']}")
    st.markdown(f"**Flight:** {data['airline']} {data['flight_number']} — {data['origin']} to {data['destination']}")
    st.markdown(f"**Departure:** {data['departure_date']} at {data['departure_time']}")
    st.markdown(f"**Seat:** {data['seat_number']} ({data['seat_preference']})")
    st.markdown(f"**Total Paid:** {format_currency(data['total_price'], data['currency'])}")
    st.markdown(f"**Payment Method:** {data['payment_method']}")

    if qrcode is not None and Image is not None:
        qr = qrcode.make(f"{data['booking_ref']}|{data['flight_number']}")
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        st.image(buffer, caption='Booking QR Code', width=170)
    else:
        st.info('Install qrcode and pillow to enable QR code generation.')

    if FPDF is not None:
        pdf_bytes = generate_ticket_pdf(data)
        if pdf_bytes:
            st.download_button('Download Ticket PDF', pdf_bytes, file_name=f"SkyFlow_{data['booking_ref']}.pdf", mime='application/pdf')
    else:
        st.info('Install fpdf to enable PDF ticket downloads.')

    col1, col2, col3, col4 = st.columns(4)
    if col1.button('Home'):
        st.session_state['page'] = 'Home'
        st.session_state['booking_stage'] = None
        st.rerun()
    if col2.button('Search Flights'):
        st.session_state['page'] = 'Search Flights'
        st.session_state['booking_stage'] = None
        st.rerun()
    if col3.button('Track Flight'):
        st.session_state['page'] = 'Track Flight'
        st.session_state['track_ref'] = data['booking_ref']
        st.rerun()
    if col4.button('My Bookings'):
        st.session_state['page'] = 'My Bookings'
        st.session_state['booking_stage'] = None
        st.rerun()


def track_flight():
    st.subheader('Track Flight')
    reference = st.text_input('Enter Booking Reference', value=st.session_state.get('track_ref', ''), key='track_reference')
    if st.button('Search', use_container_width=True):
        if not reference.strip():
            st.error('Please enter a booking reference.')
            return
        booking = db.get_booking_by_ref(reference.strip())
        if not booking:
            st.error('No booking was found for that reference.')
            return
        flight = db.get_flight_by_id(booking[3])
        st.markdown(f"**Booking Reference:** {booking[1]}")
        st.markdown(f"**Passenger:** {booking[5]}")
        st.markdown(f"**Status:** {booking[15].title()}")
        if flight:
            st.markdown(f"**Flight:** {flight[2]} {flight[1]}")
            st.markdown(f"**Route:** {flight[3]} → {flight[4]}")
            st.markdown(f"**Departure:** {flight[5]} at {flight[6]}")
            st.markdown(f"**Arrival:** {flight[7]}")
        st.progress(60)
        st.success('Flight is on schedule. Check back for updates as travel time approaches.')


def schedule_page():
    st.subheader('Flight Schedule')
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox('From', ['Any'] + LOCATIONS, key='schedule_origin')
    with col2:
        destination = st.selectbox('To', ['Any'] + LOCATIONS, key='schedule_destination')

    airline = st.selectbox('Airline', ['Any'] + db.get_distinct_airlines(), key='schedule_airline')
    flight_date = st.date_input('Departure Date', value=today, key='schedule_date')

    flights = db.get_all_flights()
    filtered = []
    for f in flights:
        if origin != 'Any' and f[3] != origin:
            continue
        if destination != 'Any' and f[4] != destination:
            continue
        if airline != 'Any' and f[2] != airline:
            continue
        if f[5] != flight_date.strftime('%Y-%m-%d'):
            continue
        filtered.append(f)

    if filtered:
        st.markdown(f"### {len(filtered)} Flights Scheduled")
        for f in filtered:
            with st.container():
                st.markdown('---')
                st.markdown(f"**{f[2]}** {f[1]} — {f[3]} → {f[4]}")
                st.write(f"Departure: {f[5]} {f[6]} | Arrival: {f[7]} | Seats left: {f[10]}")
                st.write(f"Price: {format_currency(f[8], st.session_state.get('currency', 'NGN'))}")
    else:
        st.info('No scheduled flights match these filters. Try changing the date or route.')


def my_bookings():
    st.subheader('My Bookings')
    bookings = db.get_user_bookings(st.session_state['user_id'])
    if not bookings:
        st.info('You have no bookings yet.')
        return
    for b in bookings:
        with st.expander(f"{b[0]} — {b[5]} | {b[7]} → {b[8]}"):
            st.markdown(f"**Booked On:** {b[3]}")
            st.markdown(f"**Status:** {b[4]}")
            st.markdown(f"**Passengers:** Adults {b[14]}, Children {b[15]}, Infants {b[16]}")
            st.markdown(f"**Price Paid:** {format_currency(b[17], st.session_state.get('currency', 'NGN'))}")
            if b[19]:
                st.markdown(f"**Return Flight:** {b[20]} | {b[21]} → {b[22]} on {b[23]}")
            if st.button('Track this flight', key=f'track_btn_{b[0]}'):
                st.session_state['page'] = 'Track Flight'
                st.session_state['track_ref'] = b[0]
                st.rerun()


def user_profile():
    st.subheader('Profile')
    st.markdown('Profile settings are currently managed via your account registration. Future updates will allow saved passengers, payment cards, and travel preferences.')


def notifications_page():
    st.subheader('Notifications')
    if st.session_state.get('notifications'):
        for note in st.session_state['notifications']:
            st.write(f'• {note}')
    else:
        st.info('No notifications available at the moment.')


def payment_history():
    st.subheader('Payment History')
    st.info('Your completed payments and invoices will appear here once you finish bookings.')


def support_page():
    st.subheader('Customer Support')
    st.write('Need help?')
    st.write('Email: support@skyflowairlines.com')
    st.write('Phone: +234 800 123 4567')
    st.write('We are available 24/7 for flight assistance and booking support.')
