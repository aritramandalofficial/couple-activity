from datetime import date
import streamlit as st
from repositories.mood_repository import MOODS, save_mood, get_mood_history
from ui.mood_view import render_mood_history

def render(me, partner):
    st.title('😊 Daily Mood Tracker')
    with st.form('mood_entry'):
        day = st.date_input('Date', value=date.today())
        mood = st.selectbox('How are you feeling?', list(MOODS))
        saved = st.form_submit_button('Save mood')
    if saved:
        save_mood(me['id'], day, mood)
        st.success('Mood saved.')
    mine, theirs = get_mood_history(me, partner)
    render_mood_history(me, partner, mine, theirs)
