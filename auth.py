import hashlib
import hmac
import secrets
import sqlite3
import streamlit as st
from database import connect, user_by_id


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 300_000)
    return f'{salt.hex()}:{digest.hex()}'


def verify_password(password, stored):
    try:
        salt_hex, expected_hex = stored.split(':', 1)
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt_hex), 300_000)
        return hmac.compare_digest(actual, bytes.fromhex(expected_hex))
    except (ValueError, TypeError):
        return False


def logout():
    st.session_state.pop('uid', None)
    st.rerun()


def require_login():
    uid = st.session_state.get('uid')
    if uid:
        me = user_by_id(uid)
        if me:
            return me
        st.session_state.pop('uid', None)

    st.title('❤️ Together')
    st.caption('Log in to your private couple activity tracker')
    login_tab, signup_tab = st.tabs(['Log in', 'Create account'])
    with login_tab:
        with st.form('login'):
            email = st.text_input('Email').strip().lower()
            password = st.text_input('Password', type='password')
            submitted = st.form_submit_button('Log in')
        if submitted:
            with connect() as con:
                found = con.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
            if found and verify_password(password, found['password_hash']):
                st.session_state.uid = found['id']
                st.rerun()
            st.error('Incorrect email or password.')
    with signup_tab:
        with st.form('signup'):
            name = st.text_input('Name').strip()
            new_email = st.text_input('Email address').strip().lower()
            pw = st.text_input('Password (12+ characters)', type='password')
            confirm = st.text_input('Confirm password', type='password')
            submitted = st.form_submit_button('Create account')
        if submitted:
            if not name or '@' not in new_email or '.' not in new_email.rsplit('@', 1)[-1]:
                st.error('Please enter a name and valid-looking email address.')
            elif len(pw) < 12:
                st.error('Use a password of at least 12 characters.')
            elif pw != confirm:
                st.error('Passwords do not match.')
            else:
                try:
                    with connect() as con:
                        result = con.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)', (name, new_email, hash_password(pw)))
                    st.session_state.uid = result.lastrowid
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error('An account with this email already exists.')
    st.stop()
