from database import connect, activity_rows

SQL = 'SELECT start_date, end_date, symptoms FROM periods WHERE user_id=? ORDER BY start_date DESC'

def save_period(user_id, start, end, symptoms):
    if end < start:
        raise ValueError('End date cannot be before start date.')
    with connect() as con:
        con.execute('''INSERT INTO periods(user_id,start_date,end_date,symptoms)
                       VALUES(?,?,?,?)''',
                    (user_id, start.isoformat(), end.isoformat(), ', '.join(symptoms)))

def get_period_history(me, partner):
    mine = activity_rows(me['id'], me['id'], 'period', SQL) or []
    theirs = (activity_rows(partner['id'], me['id'], 'period', SQL)
              if partner else None)
    return mine, theirs
