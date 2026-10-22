import sqlite3
import os

def clear_cache():
    if os.name == 'nt':
        base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        data_dir = os.path.join(base, "Cari Kitab")
    else:
        data_dir = os.path.join(os.path.expanduser('~'), ".cari_kitab")
    
    db_path = os.path.join(data_dir, "app_llm_cache.db")
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM llm_search_cache")
            conn.commit()
            conn.close()
            print(f"Success: AI search cache cleared from {db_path}")
        except Exception as e:
            print(f"Error: Could not clear cache: {e}")
    else:
        print(f"File not found: {db_path} - Cache might already be empty.")

if __name__ == "__main__":
    clear_cache()
