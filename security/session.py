from datetime import datetime, timedelta
from typing import Dict, Optional
import threading
import logging

class SessionManager:
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, Dict] = {}
        self.timeout = timedelta(minutes=timeout_minutes)
        self._start_cleanup_thread()

    def create_session(self, user_id: int, token: str) -> str:
        session_id = token
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id

    def validate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        if datetime.now() - session['last_activity'] > self.timeout:
            self.end_session(session_id)
            return False
        session['last_activity'] = datetime.now()
        return True

    def end_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def _start_cleanup_thread(self) -> None:
        def cleanup():
            while True:
                current = datetime.now()
                expired = [
                    sid for sid, session in self.sessions.items()
                    if current - session['last_activity'] > self.timeout
                ]
                for sid in expired:
                    self.end_session(sid)
                threading.Event().wait(60)
        
        threading.Thread(target=cleanup, daemon=True).start()
