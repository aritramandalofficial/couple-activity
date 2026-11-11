from datetime import date
import streamlit as st
from repositories.notes_repository import save_note, get_notes_history
from ui.notes_view import render_notes_history

def render(me, partner):
    st.title('📝 Daily Notes')
    st.caption('One note per person each day. Saving a second time updates it.')
    with st.form('note_entry'):
        day = st.date_input('Date', value=date.today())
        note = st.text_area('Your note', max_chars=5000)
        saved = st.form_submit_button('Save note')
    if saved:
        try:
            save_note(me['id'], day, note)
            st.success('Note saved.')
        except ValueError as exc:
            st.error(str(exc))
    mine, theirs = get_notes_history(me, partner)
    render_notes_history(me, partner, mine, theirs)
