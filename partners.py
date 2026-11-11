import sqlite3
import streamlit as st
from database import connect, rows, active_partner


def send_request(uid, email):
    try:
        with connect() as con:
            con.execute('BEGIN IMMEDIATE')
            me = con.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
            target = con.execute('SELECT * FROM users WHERE email=?', (email.strip().lower(),)).fetchone()
            if not me or not target or me['id'] == target['id']:
                return 'No eligible account found for that address.'
            if me['partner_id'] or target['partner_id']:
                return 'One of these accounts is already connected.'
            existing = con.execute('''SELECT id FROM partner_requests WHERE status='pending'
                  AND ((sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?))''',
                  (uid, target['id'], target['id'], uid)).fetchone()
            if existing:
                return 'A request between these accounts is already pending.'
            con.execute('INSERT INTO partner_requests(sender_id,receiver_id) VALUES(?,?)', (uid, target['id']))
        return None
    except sqlite3.IntegrityError:
        return 'Unable to send request.'


def accept_request(uid, request_id):
    with connect() as con:
        con.execute('BEGIN IMMEDIATE')
        req = con.execute("SELECT * FROM partner_requests WHERE id=? AND receiver_id=? AND status='pending'", (request_id, uid)).fetchone()
        if not req:
            return False
        sender = con.execute('SELECT partner_id FROM users WHERE id=?', (req['sender_id'],)).fetchone()
        recipient = con.execute('SELECT partner_id FROM users WHERE id=?', (uid,)).fetchone()
        if not sender or not recipient or sender['partner_id'] or recipient['partner_id']:
            return False
        con.execute('UPDATE users SET partner_id=? WHERE id=? AND partner_id IS NULL', (uid, req['sender_id']))
        con.execute('UPDATE users SET partner_id=? WHERE id=? AND partner_id IS NULL', (req['sender_id'], uid))
        # Acceptance is explicit consent by both members to share all four categories.
        # Owners may revoke any category later via Privacy & Profile.
        con.execute('''UPDATE users
                       SET share_weight=1, share_period=1, share_mood=1, share_notes=1
                       WHERE id IN (?, ?)''', (uid, req['sender_id']))
        con.execute("UPDATE partner_requests SET status='accepted' WHERE id=?", (req['id'],))
        con.execute('''UPDATE partner_requests SET status='cancelled' WHERE status='pending' AND id<>?
                       AND (sender_id IN (?,?) OR receiver_id IN (?,?))''',
                    (req['id'], uid, req['sender_id'], uid, req['sender_id']))
        return True


def disconnect(uid):
    with connect() as con:
        con.execute('BEGIN IMMEDIATE')
        me = con.execute('SELECT partner_id FROM users WHERE id=?', (uid,)).fetchone()
        if not me or me['partner_id'] is None:
            return
        pid = me['partner_id']
        # Revoke both sides' sharing, even for disconnected users.
        con.execute('''UPDATE users SET partner_id=NULL, share_weight=0, share_period=0,
                        share_mood=0, share_notes=0 WHERE id IN (?,?)''', (uid, pid))
        con.execute('''UPDATE partner_requests SET status='cancelled' WHERE status='pending'
                        AND (sender_id IN (?,?) OR receiver_id IN (?,?))''', (uid, pid, uid, pid))


def render(me):
    st.title('💌 Partner Requests')
    partner = active_partner(me)
    if partner:
        st.success(f"Connected with {partner['name']} ({partner['email']})")
        st.caption('When connected, both histories are shared according to each person’s privacy settings. You can turn off any category under Privacy & Profile.')
        if st.button('Disconnect partner', type='secondary'):
            disconnect(me['id'])
            st.rerun()
        return

    st.info('By requesting a connection, you agree that if your partner accepts, your existing and future weight, mood, notes and period histories will be visible to them. You can turn off individual categories later.')
    st.subheader('Send a request')
    with st.form('request'):
        target = st.text_input("Partner's registered email address").strip().lower()
        submit = st.form_submit_button('Send request')
    if submit:
        problem = send_request(me['id'], target)
        if problem:
            st.error(problem)
        else:
            st.success('Request sent. Your partner can accept it in their own account.')
            st.rerun()

    incoming = rows('''SELECT r.id,u.name,u.email FROM partner_requests r
        JOIN users u ON u.id=r.sender_id WHERE r.receiver_id=? AND r.status='pending' ORDER BY r.id DESC''', (me['id'],))
    st.subheader('Incoming requests')
    if not incoming:
        st.info('No incoming requests.')
    for req in incoming:
        st.write(f"**{req['name']}** ({req['email']}) wants to connect.")
        st.warning('Accepting shares both partners’ existing and future weight, mood, daily notes and period records. Either partner can disable a category later.')
        a, b = st.columns(2)
        if a.button('Accept', key=f"accept_{req['id']}"):
            if accept_request(me['id'], req['id']):
                st.rerun()
            st.error('Request is no longer valid.')
        if b.button('Decline', key=f"decline_{req['id']}"):
            with connect() as con:
                con.execute("UPDATE partner_requests SET status='declined' WHERE id=? AND receiver_id=? AND status='pending'", (req['id'], me['id']))
            st.rerun()

    sent = rows('''SELECT r.id,u.email FROM partner_requests r JOIN users u ON u.id=r.receiver_id
       WHERE r.sender_id=? AND r.status='pending' ORDER BY r.id DESC''', (me['id'],))
    if sent:
        st.subheader('Sent requests')
        for req in sent:
            st.write(f"Pending: {req['email']}")
            if st.button('Cancel request', key=f"cancel_{req['id']}"):
                with connect() as con:
                    con.execute("UPDATE partner_requests SET status='cancelled' WHERE id=? AND sender_id=? AND status='pending'", (req['id'], me['id']))
                st.rerun()
