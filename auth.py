import streamlit as st
import database as db

def login():
    st.subheader("🔐 Login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", use_container_width=True, key="login_button"):
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            conn = db.get_connection()
            cursor = conn.cursor()
            hashed = db.hash_password(password)
            
            # Debug: Show what we're looking for
            print(f"Looking for user: {username}")
            print(f"With hashed password: {hashed}")
            
            cursor.execute("SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?", (username, hashed))
            user = cursor.fetchone()
            
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.full_name = user[2]
                st.session_state.role = user[3]
                st.success(f"Welcome {user[2]}!")
                st.rerun()
            else:
                # Check if user exists but password wrong
                cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                user_exists = cursor.fetchone()
                if user_exists:
                    st.error("Wrong password. Please try again.")
                else:
                    st.error("Username not found. Please register first.")
            
            conn.close()

def register():
    st.subheader("📝 Register")
    
    username = st.text_input("Username", key="reg_username")
    full_name = st.text_input("Full Name", key="reg_fullname")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
    
    if st.button("Register", use_container_width=True, key="register_button"):
        # Validation
        if not username or not full_name or not email or not password:
            st.error("Please fill in all fields")
        elif password != confirm:
            st.error("Passwords do not match")
        elif len(password) < 4:
            st.error("Password must be at least 4 characters")
        else:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                st.error(f"Username '{username}' already exists. Please choose another.")
            else:
                hashed = db.hash_password(password)
                try:
                    cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, 'user')", 
                                   (username, hashed, full_name, email))
                    conn.commit()
                    st.success(f"Registration successful! Please login with username: {username}")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
            
            conn.close()

def logout():
    for key in ['logged_in', 'user_id', 'username', 'full_name', 'role']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()