from datetime import date
import streamlit as st
from repositories.period_repository import save_period, get_period_history
from ui.period_view import render_period_history

SYMPTOMS = ['Cramps','Headache','Bloating','Mood changes','Fatigue','Back pain','Other']

def render(me, partner):
    st.title('🌸 Period Tracker')
    with st.form('period_entry'):
        start = st.date_input('Start date', value=date.today(), key='period_start')
        end = st.date_input('End date', value=date.today(), key='period_end')
        symptoms = st.multiselect('Symptoms (optional)', SYMPTOMS)
        saved = st.form_submit_button('Save period')
    if saved:
        try:
            save_period(me['id'], start, end, symptoms)
            st.success('Period saved.')
        except ValueError as exc:
            st.error(str(exc))
    mine, theirs = get_period_history(me, partner)
    render_period_history(me, partner, mine, theirs)
