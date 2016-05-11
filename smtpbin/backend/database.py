import contextlib
import datetime
import sqlite3

from .migration import MIGRATIONS


class DataBase(object):
    def __init__(self, uri='messages.db'):
        self._conn = sqlite3.connect(uri)

        self._upgrade()

    def _upgrade(self):
        cur = self._conn.cursor()
        try:
            cur.execute("SELECT * FROM _version")
            [current_version] = cur.fetchone() or (0,)
            cur.close()
        except sqlite3.OperationalError:
            current_version = 0

        for version, migration in MIGRATIONS:
            if version > current_version:
                for query in migration:
                    self._conn.execute(query)
                self._conn.execute("UPDATE _version SET version = ?", (version,))
                self._conn.commit()

    @contextlib.contextmanager
    def cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def add_message(self, fromaddr, toaddr, subject, body):
        self._conn.execute("INSERT INTO messages (received, fromaddr, toaddr, subject, body) VALUES (?, ?, ?, ?, ?)",
                           (datetime.datetime.now(), fromaddr, toaddr, subject, body))
        self._conn.commit()

    def count_messages(self):
        with self.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM messages;")
            return cur.fetchone()
