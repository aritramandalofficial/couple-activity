import streamlit as st
from auth import require_login, logout
from database import init_db, active_partner
from partners import render as render_partners
from profile import render as render_profile
from pages import weight, mood, notes, period
from ui.dashboard_view import render_dashboard

st.set_page_config(page_title='Together ❤️', page_icon='❤️', layout='wide')
init_db()
me = require_login()
partner = active_partner(me)

st.sidebar.title('❤️ Together')
st.sidebar.caption(f"Signed in as {me['name']}")
page = st.sidebar.radio('Navigation', [
    'Dashboard', 'Weight Tracker', 'Daily Mood', 'Daily Notes',
    'Period Tracker', 'Partner Requests', 'Privacy & Profile'
])
if st.sidebar.button('Log out'):
    logout()

if page == 'Partner Requests':
    render_partners(me)
elif page == 'Privacy & Profile':
    render_profile(me)
elif page == 'Weight Tracker':
    weight.render(me, partner)
elif page == 'Daily Mood':
    mood.render(me, partner)
elif page == 'Daily Notes':
    notes.render(me, partner)
elif page == 'Period Tracker':
    period.render(me, partner)
else:
    render_dashboard(me, partner)
