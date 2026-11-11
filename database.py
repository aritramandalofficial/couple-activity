import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / 'couple_activity.db'

def connect():
    con = sqlite3.connect(DB, timeout=20)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA busy_timeout=20000')
    return con

def init_db():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            partner_id INTEGER REFERENCES users(id),
            share_weight INTEGER NOT NULL DEFAULT 0,
            share_period INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS partner_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL REFERENCES users(id),
            receiver_id INTEGER NOT NULL REFERENCES users(id),
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            recorded_date TEXT NOT NULL,
            weight_kg REAL NOT NULL CHECK(weight_kg > 0),
            UNIQUE(user_id, recorded_date)
        );
        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            symptoms TEXT NOT NULL DEFAULT '',
            CHECK(end_date >= start_date)
        );
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            recorded_date TEXT NOT NULL,
            mood TEXT NOT NULL,
            score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
            UNIQUE(user_id, recorded_date)
        );
        CREATE TABLE IF NOT EXISTS daily_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            recorded_date TEXT NOT NULL,
            body TEXT NOT NULL CHECK(length(body) <= 5000),
            UNIQUE(user_id, recorded_date)
        );
        ''')
        # Backwards-compatible migration: existing app.py database and passwords are preserved.
        columns = {row['name'] for row in con.execute('PRAGMA table_info(users)')}
        for column in ('share_mood', 'share_notes'):
            if column not in columns:
                con.execute(f'ALTER TABLE users ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0')

def rows(sql, params=()):
    with connect() as con:
        return [dict(x) for x in con.execute(sql, params).fetchall()]

def user_by_id(uid):
    with connect() as con:
        r = con.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
        return dict(r) if r else None

def active_partner(me):
    if me is None or me['partner_id'] is None:
        return None
    p = user_by_id(me['partner_id'])
    return p if p and p['partner_id'] == me['id'] else None

def may_view(owner_id, viewer_id, activity):
    # Server-side check; NEVER trust an input containing a chosen user's ID.
    fields = {'weight': 'share_weight', 'mood': 'share_mood', 'notes': 'share_notes', 'period': 'share_period'}
    if activity not in fields:
        return False
    if owner_id == viewer_id:
        return True
    with connect() as con:
        r = con.execute(f'''SELECT a.id FROM users a JOIN users b ON a.partner_id=b.id AND b.partner_id=a.id
            WHERE a.id=? AND b.id=? AND a.{fields[activity]}=1''', (owner_id, viewer_id)).fetchone()
    return r is not None

def activity_rows(owner_id, viewer_id, activity, sql, params=()):
    if not may_view(owner_id, viewer_id, activity):
        return None
    return rows(sql, (owner_id, *params))
