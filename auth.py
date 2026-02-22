import sqlite3
import hashlib
import streamlit as st

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
def connect_db():
    return sqlite3.connect("users.db", check_same_thread=False)


# --------------------------------------------------
# CREATE USERS TABLE
# --------------------------------------------------
def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# HASH PASSWORD
# --------------------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------
def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------
def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()

    return user


# --------------------------------------------------
# AUTH UI
# --------------------------------------------------
def authentication_ui():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        st.markdown("## 🔐 Welcome to IPL Analytics AI")

        option = st.radio("Select Option", ["Login", "Signup"])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if option == "Signup":
            if st.button("Create Account"):
                if register_user(username, password):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already exists.")

        if option == "Login":
            if st.button("Login"):
                user = login_user(username, password)

                if user:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        return False

    return True


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
def logout():
    if st.sidebar.button("Logout 🔓"):
        st.session_state.authenticated = False
        st.rerun()
