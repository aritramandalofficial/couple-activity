import streamlit as st
from ui.shared import combined_frame, share_notice

def render_mood_history(me, partner, mine, theirs):
    st.subheader('📈 Couple Daily Mood')
    frame = combined_frame(mine, theirs, me['name'], partner['name'] if partner else '',
                           'recorded_date', ['mood','score'])
    if frame.empty:
        st.info('No mood entries yet.')
    else:
        wide = frame.pivot_table(index='recorded_date', columns='Person',
                                 values='score', aggfunc='last').sort_index()
        st.line_chart(wide, height=350, y_label='Mood score (1–5)')
        table = frame.rename(columns={'recorded_date':'Date', 'mood':'Mood', 'score':'Score'})
        table['Date'] = table['Date'].dt.date
        st.subheader('📋 Daily Mood History')
        st.dataframe(table.sort_values('Date', ascending=False),
                     use_container_width=True, hide_index=True)
    share_notice(partner, theirs, 'mood')
