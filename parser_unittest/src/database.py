import sqlite3
from typing import Optional, List, Dict, Any


class DatabaseRepository:

    MAX_NAME_LEN = 256
    MAX_MESSAGE_LEN = 8096

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row   
        self._create_table()

    def _create_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
        self.conn.commit()

    @staticmethod
    def _check_int(value: Any, field: str) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{field} must be int")

    @staticmethod
    def _check_str(value: Any, field: str, min_len: int, max_len: int) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be str")
        if not (min_len <= len(value) <= max_len):
            raise ValueError(f"{field} length must be {min_len}..{max_len}")

    # ---------- CRUD ----------
    def get_by_id(self, comment_id: int) -> Optional[Dict[str, Any]]:
        self._check_int(comment_id, "comment_id")
        cur = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE id = ?",
            (comment_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_by_name(self, username: str) -> List[Dict[str, Any]]:
        self._check_str(username, "username", 1, self.MAX_NAME_LEN)
        cur = self.conn.execute(
            "SELECT id, name, message FROM comments WHERE name = ?",
            (username,),
        )
        return [dict(r) for r in cur.fetchall()]

    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._check_int(comment_id, "comment_id")
        self._check_str(username, "username", 1, self.MAX_NAME_LEN)
        self._check_str(message, "message", 1, self.MAX_MESSAGE_LEN)

        try:
            self.conn.execute(
                "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
                (comment_id, username, message),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Comment with id {comment_id} already exists") from e

    def update(self, comment_id: int, new_message: str) -> bool:
        self._check_int(comment_id, "comment_id")
        self._check_str(new_message, "new_message", 1, self.MAX_MESSAGE_LEN)

        cur = self.conn.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self.conn.commit()
        return cur.rowcount > 0   # False, если ID не найден

    def delete(self, comment_id: int) -> bool:
        self._check_int(comment_id, "comment_id")
        cur = self.conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def close(self) -> None:
        self.conn.close()