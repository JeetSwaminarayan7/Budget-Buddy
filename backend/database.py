import os

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:testpass@localhost:5432/budget_buddy_test",
)

DEFAULT_CATEGORIES = [
    ("Groceries",     "🛒", "#16A34A"),
    ("Transport",     "🚌", "#2563EB"),
    ("Dining",        "🍽️", "#D97706"),
    ("Entertainment", "🎬", "#7C3AED"),
    ("Utilities",     "💡", "#0891B2"),
    ("Housing",       "🏠", "#DC2626"),
    ("Healthcare",    "🏥", "#DB2777"),
    ("Shopping",      "🛍️", "#EA580C"),
    ("Education",     "📚", "#059669"),
    ("Income",        "💰", "#16A34A"),
]


class Connection:
    """
    Thin wrapper around a psycopg2 connection that adds an sqlite3-style
    `.execute()` shortcut directly on the connection object (psycopg2 only
    supports `.execute()` on a cursor, not the connection itself).

    Using `psycopg2.extras.DictCursor` means rows returned behave like
    both a tuple (`row[0]`) and a dict (`row["column"]`) -- matching how
    `sqlite3.Row` behaved in the previous SQLite version of this app, so
    the rest of the codebase didn't need every row-access call site
    rewritten, only the query placeholders and a few Postgres-specific
    syntax differences (see app.py).
    """

    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=None):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, params or ())
        return cur

    def cursor(self):
        return self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return Connection(conn)


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               SERIAL PRIMARY KEY,
            username         TEXT    NOT NULL UNIQUE,
            email            TEXT    NOT NULL UNIQUE,
            password         TEXT    NOT NULL,
            monthly_budget   REAL    NOT NULL DEFAULT 1000,
            savings_goal     REAL    NOT NULL DEFAULT 500,
            created_at       TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id      SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name    TEXT    NOT NULL,
            icon    TEXT    NOT NULL DEFAULT '💳',
            color   TEXT    NOT NULL DEFAULT '#6366f1',
            UNIQUE(user_id, name)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            type        TEXT    NOT NULL CHECK(type IN ('debit','credit')),
            category_id INTEGER REFERENCES categories(id),
            source      TEXT    NOT NULL DEFAULT 'manual',
            created_at  TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            amount      REAL    NOT NULL,
            month       TEXT    NOT NULL,
            UNIQUE(user_id, category_id, month)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS monthly_budgets (
            id      SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            month   TEXT    NOT NULL,
            amount  REAL    NOT NULL,
            UNIQUE(user_id, month)
        )
    """)

    conn.commit()
    conn.close()


def create_default_categories(user_id, conn):
    for name, icon, color in DEFAULT_CATEGORIES:
        conn.execute(
            """INSERT INTO categories (user_id, name, icon, color)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (user_id, name) DO NOTHING""",
            (user_id, name, icon, color),
        )
