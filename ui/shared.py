import pandas as pd
import streamlit as st

def combined_frame(mine, theirs, my_name, partner_name, date_col, value_cols):
    # Build combined history without filling missing observations with zeros.
    parts = []
    for data, label in ((mine, f'You ({my_name})'), (theirs, partner_name)):
        if data is not None and data:
            df = pd.DataFrame(data).copy()
            df['Person'] = label
            df[date_col] = pd.to_datetime(df[date_col])
            parts.append(df)
    columns = [date_col, 'Person', *value_cols]
    if not parts:
        return pd.DataFrame(columns=columns)
    return pd.concat(parts, ignore_index=True)[columns].sort_values(date_col)

def share_notice(partner, theirs, category):
    if not partner:
        st.info(f'Connect with a partner to see their {category} history here.')
    elif theirs is None:
        st.info(f"{partner['name']} has disabled sharing for {category}.")
