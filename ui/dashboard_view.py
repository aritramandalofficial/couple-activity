import streamlit as st
from repositories.weight_repository import get_weight_history
from ui.weight_view import render_weight_history

def render_dashboard(me, partner):
    st.title(f"❤️ Welcome, {me['name']}!")
    st.metric('Partner', partner['name'] if partner else 'Not connected')
    if not partner:
        st.info('Open Partner Requests to connect another registered account.')
    else:
        st.success(f"Connected with {partner['name']}")
    mine, theirs = get_weight_history(me, partner)
    render_weight_history(me, partner, mine, theirs)
    st.caption('Open each tracker for the complete combined activity history.')
