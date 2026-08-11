"""
Run this BEFORE recording the demo.
Wipes the database and seeds categories + budget limits only (no transactions).
Usage: python reset_for_demo.py
"""

import os
import sqlite3
from database import DB_PATH, init_db

# ── 1. Delete existing DB ────────────────────────────────────────────────────
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Deleted: {DB_PATH}")

# ── 2. Recreate schema ───────────────────────────────────────────────────────
init_db()
print("Schema created.")

# ── 3. Seed categories ───────────────────────────────────────────────────────
CATEGORIES = [
    ("Housing",       "🏠", "#6366f1"),
    ("Groceries",     "🛒", "#10b981"),
    ("Transport",     "🚗", "#f59e0b"),
    ("Dining",        "🍽️", "#ef4444"),
    ("Entertainment", "🎬", "#8b5cf6"),
    ("Utilities",     "⚡", "#06b6d4"),
    ("Healthcare",    "💊", "#84cc16"),
    ("Shopping",      "🛍️", "#f97316"),
    ("Income",        "💰", "#34d399"),
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

for name, icon, color in CATEGORIES:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (name, icon, color) VALUES (?, ?, ?)",
        (name, icon, color)
    )
conn.commit()
print("Categories seeded.")

conn.commit()
conn.close()
print("\nDone! Budget limits will be auto-created when you upload any statement.")
print("You can now start the backend and begin recording.")
