from database import connect, activity_rows

SQL = 'SELECT recorded_date, mood, score FROM moods WHERE user_id=? ORDER BY recorded_date'
MOODS = {'😞 Very low': 1, '😕 Low': 2, '😐 Okay': 3, '🙂 Good': 4, '😄 Great': 5}

def save_mood(user_id, day, mood):
    with connect() as con:
        con.execute('''INSERT INTO moods(user_id,recorded_date,mood,score) VALUES(?,?,?,?)
                       ON CONFLICT(user_id,recorded_date)
                       DO UPDATE SET mood=excluded.mood,score=excluded.score''',
                    (user_id, day.isoformat(), mood, MOODS[mood]))

def get_mood_history(me, partner):
    mine = activity_rows(me['id'], me['id'], 'mood', SQL) or []
    theirs = (activity_rows(partner['id'], me['id'], 'mood', SQL)
              if partner else None)
    return mine, theirs
