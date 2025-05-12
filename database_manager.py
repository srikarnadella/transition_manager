import sqlite3
from pathlib import Path

# db file name
DB_PATH = Path(__file__).parent / "song_transitions.db"

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._migrate_table()

    def _migrate_table(self):
        cursor = self.conn.cursor()
        #checks if transitions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transitions'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(transitions)")
            existing = {row[1] for row in cursor.fetchall()}
            required = {"from_artist", "from_title", "to_artist", "to_title", "note"}
            if not required.issubset(existing):
                with self.conn:
                    self.conn.execute("DROP TABLE transitions")
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_artist TEXT NOT NULL,
                    from_title  TEXT NOT NULL,
                    to_artist   TEXT NOT NULL,
                    to_title    TEXT NOT NULL,
                    note        TEXT
                );
            """)

    def add_transition(self, from_artist: str, from_title: str,
                       to_artist: str, to_title: str,
                       note: str):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO transitions
                  (from_artist, from_title, to_artist, to_title, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (from_artist, from_title, to_artist, to_title, note)
            )

    def get_all_transitions(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, from_artist, from_title, to_artist, to_title, note
              FROM transitions
             ORDER BY id
        """)
        return cursor.fetchall()
