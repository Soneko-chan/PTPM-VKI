import sqlite3
import os


class DatabaseManager:
    
    def __init__(self, db_name="registrations.db"):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    confirm_password_hash TEXT NOT NULL,
                    result TEXT NOT NULL,
                    message TEXT,
                    UNIQUE(login, password_hash, confirm_password_hash)
                )
            """)

    def add_record(self, login, password, confirm_password, result, message):
        import hashlib
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        with self._get_connection() as conn:
            try:
                conn.execute(
                    "INSERT INTO registrations (login, password_hash, confirm_password_hash, result, message) VALUES (?, ?, ?, ?, ?)",
                    (login, pwd_hash, conf_hash, result, message)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Запись уже существует

    def get_record(self, login, password, confirm_password):
        import hashlib
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT result, message FROM registrations WHERE login=? AND password_hash=? AND confirm_password_hash=?",
                (login, pwd_hash, conf_hash)
            )
            row = cursor.fetchone()
            return row  # (result, message) или None

    def delete_record(self, login, password, confirm_password):
        import hashlib
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM registrations WHERE login=? AND password_hash=? AND confirm_password_hash=?",
                (login, pwd_hash, conf_hash)
            )
            conn.commit()
            return cursor.rowcount > 0