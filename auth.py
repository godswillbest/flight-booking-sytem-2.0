import streamlit as st
import database as db

def show_login():
    st.subheader("🔐 Login to Your Account")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, key="login_button"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                conn = db.get_connection()
                cursor = conn.cursor()
                hashed = db.hash_password(password)
                cursor.execute("SELECT id, username, full_name, email, role FROM users WHERE username = ? AND password = ?", 
                              (username, hashed))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user[0]
                    st.session_state['username'] = user[1]
                    st.session_state['full_name'] = user[2]
                    st.session_state['user_email'] = user[3]
                    st.session_state['role'] = user[4]
                    st.success(f"Welcome back, {user[2]}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_register():
    st.subheader("📝 Create New Account")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("Choose Username", key="reg_username")
        full_name = st.text_input("Full Name", key="reg_fullname")
        email = st.text_input("Email Address", key="reg_email")
        password = st.text_input("Choose Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", use_container_width=True, key="register_button"):
            if not username or not full_name or not email or not password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters")
            else:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    st.error("Username already taken. Please choose another.")
                else:
                    hashed = db.hash_password(password)
                    cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, 'user')",
                                  (username, hashed, full_name, email))
                    conn.commit()
                    st.success("Account created successfully! Please login.")
                    st.balloons()
                conn.close()

def logout():
    for key in ['logged_in', 'user_id', 'username', 'full_name', 'user_email', 'role', 'selected_flight_id', 'selected_return_flight_id', 'booking_details', 'selected_outbound_id', 'selected_return_id', 'booking_stage', 'confirmation_data', 'track_ref', 'page']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['page'] = 'Home'
    st.rerun()