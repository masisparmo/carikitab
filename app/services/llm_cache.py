import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class LLMCache:
    def __init__(self, db_path=None):
        if db_path is None:
            import os
            if os.name == 'nt':
                base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
                data_dir = os.path.join(base, "Cari Kitab")
            else:
                data_dir = os.path.join(os.path.expanduser('~'), ".cari_kitab")
            
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "app_llm_cache.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_search_cache (
                    original_query TEXT PRIMARY KEY,
                    response_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hit_count INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def get_cache(self, query: str) -> dict | None:
        """Fetch cached JSON if it exists and varies by TTL 30 days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT response_json, created_at FROM llm_search_cache WHERE original_query = ?', (query,))
            row = cursor.fetchone()
            
            if row:
                response_json, created_at_str = row
                created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                # Check TTL 30 days
                if datetime.now() - created_at < timedelta(days=30):
                    # Update hit count
                    cursor.execute('UPDATE llm_search_cache SET hit_count = hit_count + 1 WHERE original_query = ?', (query,))
                    conn.commit()
                    try:
                        return json.loads(response_json)
                    except json.JSONDecodeError:
                        return None
                else:
                    # Expired, delete it
                    cursor.execute('DELETE FROM llm_search_cache WHERE original_query = ?', (query,))
                    conn.commit()
        return None

    def set_cache(self, query: str, response_dict: dict):
        """Save a new LLM response to the cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            response_json = json.dumps(response_dict, ensure_ascii=False)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO llm_search_cache (original_query, response_json, created_at, hit_count)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(original_query) DO UPDATE SET
                    response_json=excluded.response_json,
                    created_at=excluded.created_at,
                    hit_count=0
            ''', (query, response_json, now_str))
            conn.commit()

llm_cache = LLMCache()
