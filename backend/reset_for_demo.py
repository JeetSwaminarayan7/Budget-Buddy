"""
Run this BEFORE recording a demo.
Wipes the database and recreates a clean schema (no transactions, no
categories other than what get_default_categories() sets up per-user at
registration time).
Usage: python reset_for_demo.py
"""

from database import get_db, init_db

# ── Drop and recreate schema ─────────────────────────────────────────────────
conn = get_db()
conn.execute(
    "DROP TABLE IF EXISTS budgets, monthly_budgets, transactions, categories, users CASCADE"
)
conn.commit()
conn.close()
print("Dropped existing tables.")

init_db()
print("Schema recreated.")

print("\nDone! Register a fresh user to get default categories, then start")
print("the backend and begin recording.")
