from database import connect, activity_rows

SQL = 'SELECT recorded_date, body FROM daily_notes WHERE user_id=? ORDER BY recorded_date'

def save_note(user_id, day, note):
    if not note.strip():
        raise ValueError('Please write a note before saving.')
    if len(note) > 5000:
        raise ValueError('Notes must be at most 5000 characters.')
    with connect() as con:
        con.execute('''INSERT INTO daily_notes(user_id,recorded_date,body) VALUES(?,?,?)
                       ON CONFLICT(user_id,recorded_date)
                       DO UPDATE SET body=excluded.body''',
                    (user_id, day.isoformat(), note.strip()))

def get_notes_history(me, partner):
    mine = activity_rows(me['id'], me['id'], 'notes', SQL) or []
    theirs = (activity_rows(partner['id'], me['id'], 'notes', SQL)
              if partner else None)
    return mine, theirs
