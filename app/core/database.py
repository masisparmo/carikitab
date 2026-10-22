import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            import os
            import sys
            if os.name == 'nt':
                base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
                data_dir = os.path.join(base, "Cari Kitab")
            else:
                data_dir = os.path.join(os.path.expanduser('~'), ".cari_kitab")
            
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "app_history.db")
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul_arab TEXT,
                    judul_indonesia TEXT,
                    penulis_arab TEXT,
                    penulis_indonesia TEXT,
                    tanggal_download DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lokasi_file TEXT,
                    status TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    messages_json TEXT
                )
            ''')
            conn.commit()

    def add_history(self, judul_arab, judul_indonesia, penulis_arab, penulis_indonesia, lokasi_file, status="Completed"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (judul_arab, judul_indonesia, penulis_arab, penulis_indonesia, lokasi_file, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (judul_arab, judul_indonesia, penulis_arab, penulis_indonesia, lokasi_file, status))
            conn.commit()
            return cursor.lastrowid

    def get_all_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM history ORDER BY tanggal_download DESC')
            return [dict(row) for row in cursor.fetchall()]

    def update_history_status(self, history_id, status, lokasi_file=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if lokasi_file:
                cursor.execute('UPDATE history SET status = ?, lokasi_file = ? WHERE id = ?', (status, lokasi_file, history_id))
            else:
                cursor.execute('UPDATE history SET status = ? WHERE id = ?', (status, history_id))
            conn.commit()

    def delete_history(self, history_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
            conn.commit()

    # Chat Sessions
    def add_chat_session(self, title, messages_json):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_sessions (title, messages_json)
                VALUES (?, ?)
            ''', (title, messages_json))
            conn.commit()
            return cursor.lastrowid

    def get_all_chat_sessions(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chat_sessions ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    def update_chat_session(self, session_id, messages_json):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE chat_sessions SET messages_json = ? WHERE id = ?', (messages_json, session_id))
            conn.commit()

    def delete_chat_session(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
            conn.commit()

db = Database()
