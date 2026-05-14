from pathlib import Path

# Patch user.py
user_path = Path(r'c:\Coding\flight-booking-sytem-2.0\user.py')
text = user_path.read_text(encoding='utf-8')
text = text.replace("st.subheader('Find Your Flight')", "st.markdown('Search available flights using the filters below.')")
old_block = '''    if 'search_results' in st.session_state and st.session_state['search_results'] and st.session_state['trip_type'] == 'One-way':
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
                    st.session_state.pop('selected_return_flight_id', None)
                    st.session_state['booking_stage'] = 'booking'
                    st.rerun()

    if st.session_state['trip_type'] == 'Round trip':
'''
new_block = '''    if st.session_state.get('trip_type') == 'One-way':
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
                            st.session_state.pop('selected_return_flight_id', None)
                            st.session_state['booking_stage'] = 'booking'
                            st.rerun()
            else:
                st.info('No available flights were found for this route. Please adjust your filters or choose another date.')

    if st.session_state['trip_type'] == 'Round trip':
'''
if old_block not in text:
    raise ValueError('Could not find one-way search block in user.py')
text = text.replace(old_block, new_block)
old_track = '''def track_flight():
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
'''
new_track = '''def track_flight():
    st.subheader('Track Flight')
    reference = st.text_input('Enter Booking Reference or Ticket Number', value=st.session_state.get('track_ref', ''), key='track_reference')
    if st.button('Search', use_container_width=True):
        if not reference.strip():
            st.error('Please enter a booking reference or ticket number.')
            return
        booking = db.get_booking_by_ref(reference.strip())
        if not booking:
            st.error('No booking was found for that reference or ticket number.')
            return
        flight = db.get_flight_by_id(booking[3])
        st.markdown(f"**Booking Reference:** {booking[1]}")
        st.markdown(f"**Ticket Number:** {booking[2]}")
        st.markdown(f"**Passenger:** {booking[5]}")
        st.markdown(f"**Status:** {booking[15].title()}")
        if flight:
            st.markdown(f"**Flight:** {flight[2]} {flight[1]}")
            st.markdown(f"**Route:** {flight[3]} → {flight[4]}")
            st.markdown(f"**Departure:** {flight[5]} at {flight[6]}")
            st.markdown(f"**Arrival:** {flight[7]}")
        st.progress(60)
        st.success('Flight is on schedule. Check back for updates as travel time approaches.')
'''
if old_track not in text:
    raise ValueError('Could not find track_flight block in user.py')
text = text.replace(old_track, new_track)
user_path.write_text(text, encoding='utf-8')

# Patch database.py
path = Path(r'c:\Coding\flight-booking-sytem-2.0\database.py')
text = path.read_text(encoding='utf-8')
old_lookup = '''def get_booking_by_ref(reference):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_ref = ?", (reference,))
    booking = cursor.fetchone()
    conn.close()
    return booking
'''
new_lookup = '''def get_booking_by_ref(reference):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_ref = ? OR ticket_number = ?", (reference, reference))
    booking = cursor.fetchone()
    conn.close()
    return booking
'''
if old_lookup not in text:
    raise ValueError('Could not find get_booking_by_ref block in database.py')
text = text.replace(old_lookup, new_lookup)
start = text.index('        flights = [\n')
end = text.index('        cursor.executemany("""\n            INSERT INTO flights', start)
new_flights = '''        flights = [
            ('NG1001', 'Nigeria Air', 'Lagos (LOS)', 'Abuja (ABV)', day1, '06:00', '07:30', 85000, 50, 50),
            ('NG1002', 'Nigeria Air', 'Abuja (ABV)', 'Lagos (LOS)', day1, '08:00', '09:30', 85000, 50, 50),
            ('NG1003', 'Nigeria Air', 'Lagos (LOS)', 'Port Harcourt (PHC)', day2, '10:00', '11:15', 65000, 40, 40),
            ('NG1004', 'Nigeria Air', 'Port Harcourt (PHC)', 'Lagos (LOS)', day2, '12:00', '13:15', 65000, 40, 40),
            ('NG1005', 'Nigeria Air', 'Lagos (LOS)', 'Kano (KAN)', day3, '07:00', '08:45', 70000, 45, 45),
            ('NG1006', 'Nigeria Air', 'Kano (KAN)', 'Lagos (LOS)', day3, '09:30', '11:15', 70000, 45, 45),
            ('NG1007', 'Nigeria Air', 'Abuja (ABV)', 'Port Harcourt (PHC)', day7, '14:00', '15:30', 60000, 35, 35),
            ('NG1008', 'Nigeria Air', 'Port Harcourt (PHC)', 'Abuja (ABV)', day7, '16:00', '17:30', 60000, 35, 35),
            ('NG1009', 'Nigeria Air', 'Lagos (LOS)', 'Enugu (ENU)', day14, '08:00', '09:15', 55000, 40, 40),
            ('NG1010', 'Nigeria Air', 'Enugu (ENU)', 'Lagos (LOS)', day14, '10:00', '11:15', 55000, 40, 40),
            ('NG1011', 'Air Peace', 'Abuja (ABV)', 'Kano (KAN)', day2, '08:30', '10:15', 72000, 45, 45),
            ('NG1012', 'Air Peace', 'Lagos (LOS)', 'Accra (ACC)', day3, '09:45', '12:15', 160000, 55, 55),
            ('NG1013', 'Air Peace', 'Abuja (ABV)', 'Dakar (DSS)', day7, '10:00', '13:45', 250000, 50, 50),
            ('NG1014', 'Arik Air', 'Lagos (LOS)', 'Cairo (CAI)', day7, '11:00', '17:30', 280000, 45, 45),
            ('NG1015', 'Arik Air', 'Lagos (LOS)', 'London (LHR)', day14, '20:00', '06:00', 550000, 60, 60),
            ('EK2001', 'Emirates', 'Lagos (LOS)', 'Dubai (DXB)', day7, '10:00', '19:00', 450000, 80, 80),
            ('QR2002', 'Qatar Airways', 'Abuja (ABV)', 'Doha (DOH)', day7, '11:00', '20:00', 420000, 75, 75),
            ('KQ2003', 'Kenya Airways', 'Lagos (LOS)', 'Nairobi (NBO)', day7, '09:00', '14:30', 350000, 60, 60),
            ('ET2004', 'Ethiopian Airlines', 'Lagos (LOS)', 'Addis Ababa (ADD)', day14, '13:00', '19:00', 320000, 65, 65),
            ('RW2005', 'RwandAir', 'Lagos (LOS)', 'Kigali (KGL)', day14, '12:00', '16:30', 300000, 50, 50),
            ('SA2006', 'South African Airways', 'Lagos (LOS)', 'Johannesburg (JNB)', day14, '14:00', '20:00', 400000, 70, 70),
            ('LH3001', 'Lufthansa', 'Frankfurt (FRA)', 'London (LHR)', day7, '08:00', '08:55', 220000, 70, 70),
            ('BA3002', 'British Airways', 'London (LHR)', 'Paris (CDG)', day7, '10:00', '12:20', 180000, 60, 60),
            ('AC3003', 'Air Canada', 'Toronto (YYZ)', 'New York (JFK)', day7, '09:00', '11:00', 280000, 75, 75),
            ('AA3004', 'American Airlines', 'New York (JFK)', 'Los Angeles (LAX)', day14, '13:00', '16:30', 420000, 80, 80),
            ('SQ3005', 'Singapore Airlines', 'Singapore (SIN)', 'Tokyo (NRT)', day14, '09:00', '17:30', 520000, 70, 70),
            ('CX3006', 'Cathay Pacific', 'Hong Kong (HKG)', 'Bangkok (BKK)', day14, '13:00', '15:30', 260000, 70, 70),
            ('AF3007', 'Air France', 'Paris (CDG)', 'Barcelona (BCN)', day7, '12:00', '14:05', 200000, 70, 70),
            ('TK3008', 'Turkish Airlines', 'Istanbul (IST)', 'London (LHR)', day7, '11:00', '13:30', 240000, 65, 65),
            ('EK3009', 'Emirates', 'Dubai (DXB)', 'Cape Town (CPT)', day14, '22:00', '05:30', 480000, 75, 75),
            ('AF3008', 'Air France', 'Paris (CDG)', 'New York (JFK)', day14, '10:00', '13:15', 500000, 72, 72),
            ('BA3009', 'British Airways', 'London (LHR)', 'Dubai (DXB)', day7, '21:00', '07:00', 520000, 70, 70),
            ('DL3010', 'Delta Airlines', 'New York (JFK)', 'Atlanta (ATL)', day2, '14:00', '16:00', 180000, 80, 80),
            ('UA3011', 'United Airlines', 'Chicago (ORD)', 'San Francisco (SFO)', day3, '09:00', '11:30', 200000, 75, 75),
            ('AF3012', 'Air France', 'Paris (CDG)', 'Rome (FCO)', day7, '08:30', '10:20', 190000, 60, 60),
            ('EK3013', 'Emirates', 'Dubai (DXB)', 'Singapore (SIN)', day14, '02:00', '14:00', 490000, 70, 70),
            ('SQ3014', 'Singapore Airlines', 'Singapore (SIN)', 'Sydney (SYD)', day14, '15:00', '23:30', 540000, 65, 65),
            ('QF3015', 'Qantas', 'Sydney (SYD)', 'Melbourne (MEL)', day2, '08:00', '09:30', 120000, 60, 60),
            ('QF3016', 'Qantas', 'Melbourne (MEL)', 'Auckland (AKL)', day3, '10:00', '15:00', 260000, 65, 65),
            ('EK3017', 'Emirates', 'Los Angeles (LAX)', 'Dubai (DXB)', day14, '23:00', '20:00', 600000, 70, 70),
            ('AI3018', 'Air India', 'Mumbai (BOM)', 'Dubai (DXB)', day7, '13:00', '16:00', 190000, 70, 70),
            ('SQ3019', 'Singapore Airlines', 'Tokyo (NRT)', 'Singapore (SIN)', day14, '10:00', '16:00', 340000, 70, 70),
            ('NZ3020', 'Air New Zealand', 'Auckland (AKL)', 'Los Angeles (LAX)', day14, '09:00', '23:00', 580000, 68, 68),
            ('AA3021', 'American Airlines', 'Miami (MIA)', 'Buenos Aires (EZE)', day7, '17:00', '07:00', 430000, 72, 72),
            ('IB3022', 'Iberia', 'Madrid (MAD)', 'São Paulo (GRU)', day14, '19:00', '05:00', 440000, 65, 65),
            ('QR3023', 'Qatar Airways', 'Doha (DOH)', 'London (LHR)', day7, '08:00', '12:00', 300000, 70, 70),
            ('EK3024', 'Emirates', 'Dubai (DXB)', 'Johannesburg (JNB)', day14, '06:00', '12:00', 380000, 68, 68),
            ('SA3025', 'South African Airways', 'Johannesburg (JNB)', 'Cape Town (CPT)', day7, '10:00', '12:30', 150000, 60, 60),
            ('KQ3026', 'Kenya Airways', 'Nairobi (NBO)', 'Dar es Salaam (DAR)', day7, '07:00', '08:30', 160000, 55, 55),
            ('ET3027', 'Ethiopian Airlines', 'Addis Ababa (ADD)', 'Kigali (KGL)', day7, '11:00', '12:20', 140000, 55, 55),
            ('QR3028', 'Qatar Airways', 'Doha (DOH)', 'Singapore (SIN)', day14, '09:00', '21:00', 430000, 70, 70),
            ('EK3029', 'Emirates', 'Dubai (DXB)', 'New York (JFK)', day14, '10:00', '18:00', 620000, 75, 75),
            ('BA3030', 'British Airways', 'London (LHR)', 'Newark (EWR)', day7, '11:00', '14:15', 420000, 70, 70),
        ]
'''
text = text[:start] + new_flights + text[end:]
path.write_text(text, encoding='utf-8')
print('Patched user.py and database.py successfully')
from pathlib import Path

# Patch user.py
user_path = Path(r'c:\Coding\flight-booking-sytem-2.0\user.py')
text = user_path.read_text(encoding='utf-8')
text = text.replace("st.subheader('Find Your Flight')", "st.markdown('Search available flights using the filters below.')")
old_block = """    if 'search_results' in st.session_state and st.session_state['search_results'] and st.session_state['trip_type'] == 'One-way':
        for f in st.session_state['search_results']:
            with st.container():
                st.markdown('---')
                st.markdown(f\"### {f[2]} — {f[3]} → {f[4]}\")
                st.write(f\"**Departure:** {f[5]} | **Arrival:** {f[7]}\")
                st.write(f\"**Class:** Economy | **Seats left:** {f[10]}\")
                st.write(f\"**Price per seat:** {format_currency(f[8], currency)}\")
                total_cost = f[8] * seats_required
                st.write(f\"**Total cost:** {format_currency(total_cost, currency)}\")
                if st.button(f\"Book {f[1]}\", key=f\"book_btn_{f[0]}\"):
                    st.session_state['selected_flight_id'] = f[0]
                    st.session_state.pop('selected_return_flight_id', None)
                    st.session_state['booking_stage'] = 'booking'
                    st.rerun()

    if st.session_state['trip_type'] == 'Round trip':
"""
new_block = """    if st.session_state.get('trip_type') == 'One-way':
        if 'search_results' in st.session_state:
            if st.session_state['search_results']:
                for f in st.session_state['search_results']:
                    with st.container():
                        st.markdown('---')
                        st.markdown(f\"### {f[2]} — {f[3]} → {f[4]}\")
                        st.write(f\"**Departure:** {f[5]} | **Arrival:** {f[7]}\")
                        st.write(f\"**Class:** Economy | **Seats left:** {f[10]}\")
                        st.write(f\"**Price per seat:** {format_currency(f[8], currency)}\")
                        total_cost = f[8] * seats_required
                        st.write(f\"**Total cost:** {format_currency(total_cost, currency)}\")
                        if st.button(f\"Book {f[1]}\", key=f\"book_btn_{f[0]}\"):
                            st.session_state['selected_flight_id'] = f[0]
                            st.session_state.pop('selected_return_flight_id', None)
                            st.session_state['booking_stage'] = 'booking'
                            st.rerun()
            else:
                st.info('No available flights were found for this route. Please adjust your filters or choose another date.')

    if st.session_state['trip_type'] == 'Round trip':
"""
if old_block not in text:
    raise ValueError('Could not find one-way search block in user.py')
text = text.replace(old_block, new_block)

old_track = """def track_flight():
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
"""
new_track = """def track_flight():
    st.subheader('Track Flight')
    reference = st.text_input('Enter Booking Reference or Ticket Number', value=st.session_state.get('track_ref', ''), key='track_reference')
    if st.button('Search', use_container_width=True):
        if not reference.strip():
            st.error('Please enter a booking reference or ticket number.')
            return
        booking = db.get_booking_by_ref(reference.strip())
        if not booking:
            st.error('No booking was found for that reference or ticket number.')
            return
        flight = db.get_flight_by_id(booking[3])
        st.markdown(f"**Booking Reference:** {booking[1]}")
        st.markdown(f"**Ticket Number:** {booking[2]}")
        st.markdown(f"**Passenger:** {booking[5]}")
        st.markdown(f"**Status:** {booking[15].title()}")
        if flight:
            st.markdown(f"**Flight:** {flight[2]} {flight[1]}")
            st.markdown(f"**Route:** {flight[3]} → {flight[4]}")
            st.markdown(f"**Departure:** {flight[5]} at {flight[6]}")
            st.markdown(f"**Arrival:** {flight[7]}")
        st.progress(60)
        st.success('Flight is on schedule. Check back for updates as travel time approaches.')
"""
if old_track not in text:
    raise ValueError('Could not find track_flight block in user.py')
text = text.replace(old_track, new_track)

user_path.write_text(text, encoding='utf-8')

# Patch database.py
path = Path(r'c:\Coding\flight-booking-sytem-2.0\database.py')
text = path.read_text(encoding='utf-8')
old_lookup = """def get_booking_by_ref(reference):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(\"SELECT * FROM bookings WHERE booking_ref = ?\", (reference,))
    booking = cursor.fetchone()
    conn.close()
    return booking
"""
new_lookup = """def get_booking_by_ref(reference):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(\"SELECT * FROM bookings WHERE booking_ref = ? OR ticket_number = ?\", (reference, reference))
    booking = cursor.fetchone()
    conn.close()
    return booking
"""
if old_lookup not in text:
    raise ValueError('Could not find get_booking_by_ref block in database.py')
text = text.replace(old_lookup, new_lookup)

start = text.index("        flights = [\n")
end = text.index("        cursor.executemany(\"\"\"\n            INSERT INTO flights", start)
new_flights = '''        flights = [
            ('NG1001', 'Nigeria Air', 'Lagos (LOS)', 'Abuja (ABV)', day1, '06:00', '07:30', 85000, 50, 50),
            ('NG1002', 'Nigeria Air', 'Abuja (ABV)', 'Lagos (LOS)', day1, '08:00', '09:30', 85000, 50, 50),
            ('NG1003', 'Nigeria Air', 'Lagos (LOS)', 'Port Harcourt (PHC)', day2, '10:00', '11:15', 65000, 40, 40),
            ('NG1004', 'Nigeria Air', 'Port Harcourt (PHC)', 'Lagos (LOS)', day2, '12:00', '13:15', 65000, 40, 40),
            ('NG1005', 'Nigeria Air', 'Lagos (LOS)', 'Kano (KAN)', day3, '07:00', '08:45', 70000, 45, 45),
            ('NG1006', 'Nigeria Air', 'Kano (KAN)', 'Lagos (LOS)', day3, '09:30', '11:15', 70000, 45, 45),
            ('NG1007', 'Nigeria Air', 'Abuja (ABV)', 'Port Harcourt (PHC)', day7, '14:00', '15:30', 60000, 35, 35),
            ('NG1008', 'Nigeria Air', 'Port Harcourt (PHC)', 'Abuja (ABV)', day7, '16:00', '17:30', 60000, 35, 35),
            ('NG1009', 'Nigeria Air', 'Lagos (LOS)', 'Enugu (ENU)', day14, '08:00', '09:15', 55000, 40, 40),
            ('NG1010', 'Nigeria Air', 'Enugu (ENU)', 'Lagos (LOS)', day14, '10:00', '11:15', 55000, 40, 40),
            ('NG1011', 'Air Peace', 'Abuja (ABV)', 'Kano (KAN)', day2, '08:30', '10:15', 72000, 45, 45),
            ('NG1012', 'Air Peace', 'Lagos (LOS)', 'Accra (ACC)', day3, '09:45', '12:15', 160000, 55, 55),
            ('NG1013', 'Air Peace', 'Abuja (ABV)', 'Dakar (DSS)', day7, '10:00', '13:45', 250000, 50, 50),
            ('NG1014', 'Arik Air', 'Lagos (LOS)', 'Cairo (CAI)', day7, '11:00', '17:30', 280000, 45, 45),
            ('NG1015', 'Arik Air', 'Lagos (LOS)', 'London (LHR)', day14, '20:00', '06:00', 550000, 60, 60),
            ('EK2001', 'Emirates', 'Lagos (LOS)', 'Dubai (DXB)', day7, '10:00', '19:00', 450000, 80, 80),
            ('QR2002', 'Qatar Airways', 'Abuja (ABV)', 'Doha (DOH)', day7, '11:00', '20:00', 420000, 75, 75),
            ('KQ2003', 'Kenya Airways', 'Lagos (LOS)', 'Nairobi (NBO)', day7, '09:00', '14:30', 350000, 60, 60),
            ('ET2004', 'Ethiopian Airlines', 'Lagos (LOS)', 'Addis Ababa (ADD)', day14, '13:00', '19:00', 320000, 65, 65),
            ('RW2005', 'RwandAir', 'Lagos (LOS)', 'Kigali (KGL)', day14, '12:00', '16:30', 300000, 50, 50),
            ('SA2006', 'South African Airways', 'Lagos (LOS)', 'Johannesburg (JNB)', day14, '14:00', '20:00', 400000, 70, 70),
            ('LH3001', 'Lufthansa', 'Frankfurt (FRA)', 'London (LHR)', day7, '08:00', '08:55', 220000, 70, 70),
            ('BA3002', 'British Airways', 'London (LHR)', 'Paris (CDG)', day7, '10:00', '12:20', 180000, 60, 60),
            ('AC3003', 'Air Canada', 'Toronto (YYZ)', 'New York (JFK)', day7, '09:00', '11:00', 280000, 75, 75),
            ('AA3004', 'American Airlines', 'New York (JFK)', 'Los Angeles (LAX)', day14, '13:00', '16:30', 420000, 80, 80),
            ('SQ3005', 'Singapore Airlines', 'Singapore (SIN)', 'Tokyo (NRT)', day14, '09:00', '17:30', 520000, 70, 70),
            ('CX3006', 'Cathay Pacific', 'Hong Kong (HKG)', 'Bangkok (BKK)', day14, '13:00', '15:30', 260000, 70, 70),
            ('AF3007', 'Air France', 'Paris (CDG)', 'Barcelona (BCN)', day7, '12:00', '14:05', 200000, 70, 70),
            ('TK3008', 'Turkish Airlines', 'Istanbul (IST)', 'London (LHR)', day7, '11:00', '13:30', 240000, 65, 65),
            ('EK3009', 'Emirates', 'Dubai (DXB)', 'Cape Town (CPT)', day14, '22:00', '05:30', 480000, 75, 75),
            ('AF3008', 'Air France', 'Paris (CDG)', 'New York (JFK)', day14, '10:00', '13:15', 500000, 72, 72),
            ('BA3009', 'British Airways', 'London (LHR)', 'Dubai (DXB)', day7, '21:00', '07:00', 520000, 70, 70),
            ('DL3010', 'Delta Airlines', 'New York (JFK)', 'Atlanta (ATL)', day2, '14:00', '16:00', 180000, 80, 80),
            ('UA3011', 'United Airlines', 'Chicago (ORD)', 'San Francisco (SFO)', day3, '09:00', '11:30', 200000, 75, 75),
            ('AF3012', 'Air France', 'Paris (CDG)', 'Rome (FCO)', day7, '08:30', '10:20', 190000, 60, 60),
            ('EK3013', 'Emirates', 'Dubai (DXB)', 'Singapore (SIN)', day14, '02:00', '14:00', 490000, 70, 70),
            ('SQ3014', 'Singapore Airlines', 'Singapore (SIN)', 'Sydney (SYD)', day14, '15:00', '23:30', 540000, 65, 65),
            ('QF3015', 'Qantas', 'Sydney (SYD)', 'Melbourne (MEL)', day2, '08:00', '09:30', 120000, 60, 60),
            ('QF3016', 'Qantas', 'Melbourne (MEL)', 'Auckland (AKL)', day3, '10:00', '15:00', 260000, 65, 65),
            ('EK3017', 'Emirates', 'Los Angeles (LAX)', 'Dubai (DXB)', day14, '23:00', '20:00', 600000, 70, 70),
            ('AI3018', 'Air India', 'Mumbai (BOM)', 'Dubai (DXB)', day7, '13:00', '16:00', 190000, 70, 70),
            ('SQ3019', 'Singapore Airlines', 'Tokyo (NRT)', 'Singapore (SIN)', day14, '10:00', '16:00', 340000, 70, 70),
            ('NZ3020', 'Air New Zealand', 'Auckland (AKL)', 'Los Angeles (LAX)', day14, '09:00', '23:00', 580000, 68, 68),
            ('AA3021', 'American Airlines', 'Miami (MIA)', 'Buenos Aires (EZE)', day7, '17:00', '07:00', 430000, 72, 72),
            ('IB3022', 'Iberia', 'Madrid (MAD)', 'Sao Paulo (GRU)', day14, '19:00', '05:00', 440000, 65, 65),
            ('QR3023', 'Qatar Airways', 'Doha (DOH)', 'London (LHR)', day7, '08:00', '12:00', 300000, 70, 70),
            ('EK3024', 'Emirates', 'Dubai (DXB)', 'Johannesburg (JNB)', day14, '06:00', '12:00', 380000, 68, 68),
            ('SA3025', 'South African Airways', 'Johannesburg (JNB)', 'Cape Town (CPT)', day7, '10:00', '12:30', 150000, 60, 60),
            ('KQ3026', 'Kenya Airways', 'Nairobi (NBO)', 'Dar es Salaam (DAR)', day7, '07:00', '08:30', 160000, 55, 55),
            ('ET3027', 'Ethiopian Airlines', 'Addis Ababa (ADD)', 'Kigali (KGL)', day7, '11:00', '12:20', 140000, 55, 55),
            ('QR3028', 'Qatar Airways', 'Doha (DOH)', 'Singapore (SIN)', day14, '09:00', '21:00', 430000, 70, 70),
            ('EK3029', 'Emirates', 'Dubai (DXB)', 'New York (JFK)', day14, '10:00', '18:00', 620000, 75, 75),
            ('BA3030', 'British Airways', 'London (LHR)', 'Newark (EWR)', day7, '11:00', '14:15', 420000, 70, 70),
        ]
'''
text = text[:start] + new_flights + text[end:]
path.write_text(text, encoding='utf-8')
print('Patched user.py and database.py successfully')
