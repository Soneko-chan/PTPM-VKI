import sqlite3
import hashlib


class DatabaseManager:
    def __init__(self, db_name="registrations.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
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
        self.conn.commit()

    def add_record(self, login, password, confirm_password, result, message):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        try:
            self.conn.execute(
                "INSERT INTO registrations (login, password_hash, confirm_password_hash, result, message) VALUES (?, ?, ?, ?, ?)",
                (login, pwd_hash, conf_hash, result, message)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_record(self, login, password, confirm_password):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        cursor = self.conn.execute(
            "SELECT result, message FROM registrations WHERE login=? AND password_hash=? AND confirm_password_hash=?",
            (login, pwd_hash, conf_hash)
        )
        return cursor.fetchone()

    def delete_record(self, login, password, confirm_password):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conf_hash = hashlib.sha256(confirm_password.encode()).hexdigest()

        cursor = self.conn.execute(
            "DELETE FROM registrations WHERE login=? AND password_hash=? AND confirm_password_hash=?",
            (login, pwd_hash, conf_hash)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Явно закрывает соединение с БД."""
        if self.conn:
            self.conn.close()
            self.conn = None