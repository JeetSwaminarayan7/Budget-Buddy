import sqlite3
import os

DB_PATH = os.environ.get(
    "BUDGET_BUDDY_DB",
    os.path.join(os.path.dirname(__file__), "budget_buddy.db"),
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


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Detect old schema (no users table) and drop to migrate cleanly
    tables = {r[0] for r in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}

    if "categories" in tables and "users" not in tables:
        cursor.executescript(
            "DROP TABLE IF EXISTS budgets;"
            "DROP TABLE IF EXISTS transactions;"
            "DROP TABLE IF EXISTS categories;"
        )
        conn.commit()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT    NOT NULL UNIQUE,
            email            TEXT    NOT NULL UNIQUE,
            password         TEXT    NOT NULL,
            monthly_budget   REAL    NOT NULL DEFAULT 1000,
            savings_goal     REAL    NOT NULL DEFAULT 500,
            created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name    TEXT    NOT NULL,
            icon    TEXT    NOT NULL DEFAULT '💳',
            color   TEXT    NOT NULL DEFAULT '#6366f1',
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date        TEXT    NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            type        TEXT    NOT NULL CHECK(type IN ('debit','credit')),
            category_id INTEGER REFERENCES categories(id),
            source      TEXT    NOT NULL DEFAULT 'manual',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id),
            amount      REAL    NOT NULL,
            month       TEXT    NOT NULL,
            UNIQUE(user_id, category_id, month)
        );

        CREATE TABLE IF NOT EXISTS monthly_budgets (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            month   TEXT    NOT NULL,
            amount  REAL    NOT NULL,
            UNIQUE(user_id, month)
        );
    """)

    # Migrate existing users table if columns are missing
    cols = {r[1] for r in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "monthly_budget" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN monthly_budget REAL NOT NULL DEFAULT 1000")
    if "savings_goal" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN savings_goal REAL NOT NULL DEFAULT 500")

    conn.commit()
    conn.close()


def create_default_categories(user_id, conn):
    for name, icon, color in DEFAULT_CATEGORIES:
        conn.execute(
            "INSERT OR IGNORE INTO categories (user_id, name, icon, color) VALUES (?, ?, ?, ?)",
            (user_id, name, icon, color),
        )
