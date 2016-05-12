import contextlib
import datetime
import sqlite3

from .migration import MIGRATIONS


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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
        cur.row_factory = _dict_factory
        try:
            yield cur
        finally:
            self._conn.commit()
            cur.close()

    def get_messages(self, inbox):
        with self.cursor as cur:
            cur.execute("SELECT id, received, fromaddr, toaddr, subject, body "
                        "FROM messages "
                        "WHERE inbox = ?", (inbox,))
            return cur.fetchone()

    def add_message(self, inbox, fromaddr, toaddr, subject, body):
        with self.cursor() as cur:
            cur.execute("INSERT INTO messages (inbox, received, fromaddr, toaddr, subject, body) "
                        "VALUES (?, ?, ?, ?, ?, ?)", (inbox, datetime.datetime.now(), fromaddr, toaddr, subject, body))
            return cur.lastrowid

    def count_messages(self):
        with self.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS COUNT FROM messages;")
            return cur.fetchone()['COUNT']

    def get_inbox(self, name, apikey):
        with self.cursor() as cur:
            cur.execute("SELECT id, name, apikey "
                        "FROM inbox "
                        "WHERE name = ? "
                        "AND apikey = ?;", (name, apikey))
            return cur.fetchone()

    def get_inboxes(self):
        with self.cursor() as cur:
            cur.execute("SELECT id, name, apikey "
                        "FROM inbox;")
            return cur.fetchall()

    def create_inbox(self, name, apikey):
        with self.cursor() as cur:
            cur.execute("INSERT INTO inbox (name, apikey) "
                        "VALUES (?, ?)", (name, apikey))
            return cur.lastrowid
