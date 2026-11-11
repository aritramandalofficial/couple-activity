from datetime import date, timedelta
import streamlit as st
from ui.shared import combined_frame, share_notice

def render_period_history(me, partner, mine, theirs):
    st.subheader('🌸 Shared Period History')
    frame = combined_frame(mine, theirs, me['name'], partner['name'] if partner else '',
                           'start_date', ['end_date', 'symptoms'])
    if frame.empty:
        st.info('No period entries yet.')
    else:
        table = frame.rename(columns={'start_date':'Start', 'end_date':'End', 'symptoms':'Symptoms'})
        table['Start'] = table['Start'].dt.date
        table['End'] = table['End'].apply(lambda x: date.fromisoformat(x) if x else None)
        st.dataframe(table.sort_values('Start', ascending=False), use_container_width=True,
                     hide_index=True)
        # Never mix cycle lengths between two different people's period records.
        for label, records in [(f"You ({me['name']})", mine),
                               (partner['name'] if partner else '', theirs)]:
            if not records:
                continue
            starts = sorted({date.fromisoformat(r['start_date']) for r in records})
            gaps = [(b-a).days for a,b in zip(starts,starts[1:])]
            recent = [x for x in gaps if 15 <= x <= 90][-6:]
            average = round(sum(recent)/len(recent)) if recent else 28
            estimate = starts[-1] + timedelta(days=average)
            st.caption(f'{label}: estimated next start {estimate:%d %b %Y} '
                       f'({average}-day {"observed average" if recent else "assumption"}).')
        st.caption('Cycle dates are rough estimates, not medical or contraception guidance.')
    share_notice(partner, theirs, 'period')
