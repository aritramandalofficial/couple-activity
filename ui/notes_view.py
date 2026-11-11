import streamlit as st
from ui.shared import combined_frame, share_notice

def render_notes_history(me, partner, mine, theirs):
    st.subheader('📝 Combined Daily Notes')
    frame = combined_frame(mine, theirs, me['name'], partner['name'] if partner else '',
                           'recorded_date', ['body'])
    if frame.empty:
        st.info('No notes yet.')
    else:
        frame = frame.rename(columns={'recorded_date':'Date', 'body':'Note'})
        frame['Date'] = frame['Date'].dt.date
        st.dataframe(frame.sort_values(['Date','Person'], ascending=[False,True]),
                     use_container_width=True, hide_index=True)
    share_notice(partner, theirs, 'notes')
