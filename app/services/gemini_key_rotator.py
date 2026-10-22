import time
import os
import threading
from typing import Optional

class GeminiKeyRotator:
    def __init__(self):
        self.lock = threading.Lock()
        self.keys = []
        self.current_idx = 0
        self.cooldowns = {} # key -> timestamp when it becomes available again
        self.COOLDOWN_PERIOD = 300 # 5 minutes
        
        # Load keys from env
        self._load_keys()

    def reload_keys(self):
        with self.lock:
            self.keys = []
            self.current_idx = 0
            self._load_keys()

    def _load_keys(self):
        # Try loading from local .env or config file first (AppData for installed apps)
        local_keys = ""
        
        # Helper to get data dir (simplified for this file)
        import sys
        if os.name == 'nt':
            base = os.environ.get('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
            data_dir = os.path.join(base, "Cari Kitab")
        else:
            data_dir = os.path.join(os.path.expanduser('~'), ".cari_kitab")
            
        env_path = os.path.join(data_dir, ".env")
        
        # Fallback to current working directory if not in AppData (for development)
        if not os.path.exists(env_path):
            env_path_dev = os.path.join(os.getcwd(), ".env")
            if os.path.exists(env_path_dev):
                env_path = env_path_dev

        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEYS="):
                        local_keys = line.split("=", 1)[1].strip()
        
        raw_keys = local_keys if local_keys else os.environ.get("GEMINI_API_KEYS", "")
        if raw_keys:
            self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        else:
            # Check for GEMINI_API_KEY_1, _2, etc
            for k, v in os.environ.items():
                if k.startswith("GEMINI_API_KEY") and v.strip():
                    self.keys.append(v.strip())
            
        if not self.keys:
            print("WARNING: No GEMINI API Keys found. Please configure them in Settings or .env")

    def add_key(self, api_key: str):
        with self.lock:
            if api_key not in self.keys:
                self.keys.append(api_key)

    def get_key(self) -> Optional[str]:
        """Returns an available API key, or None if all are exhausted/cooldown"""
        with self.lock:
            if not self.keys:
                return None
                
            now = time.time()
            start_idx = self.current_idx
            
            while True:
                candidate = self.keys[self.current_idx]
                cooldown_until = self.cooldowns.get(candidate, 0)
                
                if now >= cooldown_until:
                    # Key is available! Provide it and advance strictly
                    key_to_return = candidate
                    self.current_idx = (self.current_idx + 1) % len(self.keys)
                    return key_to_return
                
                # Advance and check if we did a full loop
                self.current_idx = (self.current_idx + 1) % len(self.keys)
                if self.current_idx == start_idx:
                    # All keys are on cooldown
                    return None

    def report_error(self, api_key: str, status_code: int):
        """Marks a key as invalid or on cooldown based on error"""
        with self.lock:
            now = time.time()
            if status_code in (429, 403, 500, 503):
                # Apply 5 minutes cooldown
                cooldown_time = 300
                print(f"[KeyRotator] [LIMIT] Key *{api_key[-4:]} limited ({status_code}). Cooldown: {cooldown_time}s")
                self.cooldowns[api_key] = now + cooldown_time
            elif status_code in (400, 401):
                # Invalid request/key, disable for longer or permanently
                cooldown_time = 3600
                print(f"[KeyRotator] [AUTH_ERR] Key *{api_key[-4:]} AUTH ERROR ({status_code}). Cooldown: {cooldown_time}s")
                self.cooldowns[api_key] = now + cooldown_time
