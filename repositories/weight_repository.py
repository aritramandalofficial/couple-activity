from database import connect, activity_rows

SQL = 'SELECT recorded_date, weight_kg FROM weights WHERE user_id=? ORDER BY recorded_date'

def save_weight(user_id, day, kg):
    with connect() as con:
        con.execute('''INSERT INTO weights(user_id, recorded_date, weight_kg)
                       VALUES (?, ?, ?)
                       ON CONFLICT(user_id, recorded_date)
                       DO UPDATE SET weight_kg=excluded.weight_kg''',
                    (user_id, day.isoformat(), kg))

def get_weight_history(me, partner):
    mine = activity_rows(me['id'], me['id'], 'weight', SQL) or []
    theirs = (activity_rows(partner['id'], me['id'], 'weight', SQL)
              if partner else None)
    return mine, theirs
