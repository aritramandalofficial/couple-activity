import pandas as pd
import streamlit as st
from ui.shared import combined_frame, share_notice

def render_weight_history(me, partner, mine, theirs):
    st.subheader('📈 Couple Weight Progress')
    frame = combined_frame(mine, theirs, me['name'], partner['name'] if partner else '',
                           'recorded_date', ['weight_kg'])
    if frame.empty:
        st.info('No weight records available yet.')
    else:
        wide = (frame.pivot_table(index='recorded_date', columns='Person',
                                  values='weight_kg', aggfunc='last').sort_index())
        st.line_chart(wide, height=380, y_label='Weight (kg)')
        st.subheader('📋 Combined Weight History')
        table = wide.reset_index().rename(columns={'recorded_date': 'Date'})
        table['Date'] = table['Date'].dt.date
        st.dataframe(table.sort_values('Date', ascending=False),
                     use_container_width=True, hide_index=True)
        labels = [f"You ({me['name']})"]
        if partner and theirs is not None:
            labels.append(partner['name'])
        metrics = st.columns(len(labels))
        for i, label in enumerate(labels):
            series = wide[label].dropna() if label in wide.columns else pd.Series(dtype=float)
            metrics[i].metric(label, f'{series.iloc[-1]:.1f} kg' if not series.empty else 'Not recorded')
    share_notice(partner, theirs, 'weight')
