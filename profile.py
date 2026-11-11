import streamlit as st
from database import connect, active_partner


def render(me):
    st.title('🔐 Privacy & Profile')
    st.write(f"Name: **{me['name']}**")
    st.write(f"Email: **{me['email']}**")
    partner = active_partner(me)
    if not partner:
        st.info('Connect a partner to configure sharing. Your records are private by default.')
        return
    st.write(f"Connected with: **{partner['name']}**")
    st.caption('Each switch controls whether your partner can see YOUR records. You can revoke permission at any time.')
    with st.form('sharing'):
        weight = st.checkbox('Share my weight history', value=bool(me['share_weight']))
        mood = st.checkbox('Share my daily mood history', value=bool(me['share_mood']))
        notes = st.checkbox('Share my daily notes', value=bool(me['share_notes']))
        period = st.checkbox('Share my period history', value=bool(me['share_period']))
        save = st.form_submit_button('Save privacy settings')
    if st.button('Share all four histories with partner'):
        with connect() as con:
            con.execute('''UPDATE users SET share_weight=1, share_mood=1,
                           share_notes=1, share_period=1 WHERE id=? AND partner_id=?''',
                        (me['id'], partner['id']))
        st.rerun()
    if save:
        with connect() as con:
            con.execute('''UPDATE users SET share_weight=?,share_mood=?,share_notes=?,share_period=?
                       WHERE id=? AND partner_id=?''',
                       (int(weight), int(mood), int(notes), int(period), me['id'], partner['id']))
        st.success('Updated your sharing permissions.')
        st.rerun()
