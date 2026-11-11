from datetime import date
import streamlit as st
from repositories.weight_repository import save_weight, get_weight_history
from ui.weight_view import render_weight_history

def render(me, partner):
    st.title('⚖️ Weight Tracker')
    with st.form('weight_entry'):
        day = st.date_input('Date', value=date.today())
        kg = st.number_input('Your weight (kg)', min_value=1.0, max_value=500.0,
                             value=65.0, step=0.1)
        saved = st.form_submit_button('Save weight')
    if saved:
        save_weight(me['id'], day, kg)
        st.success('Weight saved.')
    mine, theirs = get_weight_history(me, partner)
    render_weight_history(me, partner, mine, theirs)
