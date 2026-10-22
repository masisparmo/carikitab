import os
import sys
from pathlib import Path

def get_data_dir():
    """ Get a writable directory for app data (logs, db, etc) """
    if os.name == 'nt':
        # %APPDATA%/Cari Kitab
        base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        data_dir = os.path.join(base, "Cari Kitab")
    else:
        # ~/.cari_kitab
        base = os.path.expanduser('~')
        data_dir = os.path.join(base, ".cari_kitab")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_writable_path(filename):
    """ Return absolute path for a writable file in the data directory """
    return os.path.join(get_data_dir(), filename)

def get_downloads_dir():
    """ Get the standard system Downloads folder, user-defined path, or fallback to AppData """
    # 1. Check if user has defined a custom path in .env
    custom_dir = os.environ.get('DOWNLOAD_DIR')
    if custom_dir and os.path.isdir(custom_dir):
        return str(Path(custom_dir).resolve())

    if os.name == 'nt':
        try:
            base = os.environ.get('USERPROFILE') or os.path.expanduser('~')
            d_dir = os.path.join(base, 'Downloads', 'Cari Kitab')
        except:
            d_dir = os.path.join(get_data_dir(), 'downloads')
    else:
        d_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'Cari Kitab')
    
    # Normalize path (remove spaces/slashes weirdness)
    d_dir = str(Path(d_dir).resolve())
    if not os.path.exists(d_dir):
        os.makedirs(d_dir, exist_ok=True)
    return d_dir
