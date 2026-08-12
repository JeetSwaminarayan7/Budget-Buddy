from database import get_db, init_db


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

TRANSACTIONS = [
    ("2025-01-24", "Tesco Superstore",     -87.43,  "debit",  "Groceries"),
    ("2025-01-24", "Salary - January",    3850.00,  "credit", "Income"),
    ("2025-01-23", "Netflix",              -17.99,  "debit",  "Entertainment"),
    ("2025-01-22", "Shell Petrol Station", -64.20,  "debit",  "Transport"),
    ("2025-01-21", "Nando's Watford",      -32.50,  "debit",  "Dining"),
    ("2025-01-20", "British Gas",          -89.00,  "debit",  "Utilities"),
    ("2025-01-19", "ASOS",                 -45.99,  "debit",  "Shopping"),
    ("2025-01-18", "Boots Pharmacy",       -12.75,  "debit",  "Healthcare"),
    ("2025-01-17", "Rent - January",      -850.00,  "debit",  "Housing"),
    ("2025-01-16", "Uber",                 -14.80,  "debit",  "Transport"),
    ("2025-01-15", "Sainsbury's",          -56.30,  "debit",  "Groceries"),
    ("2025-01-14", "Spotify",              -11.99,  "debit",  "Entertainment"),
    ("2025-01-13", "Costa Coffee",          -8.40,  "debit",  "Dining"),
    ("2025-01-12", "Thames Water",         -45.00,  "debit",  "Utilities"),
    ("2025-01-11", "TfL Oyster Top-up",    -40.00,  "debit",  "Transport"),
    ("2025-01-10", "McDonald's",           -12.30,  "debit",  "Dining"),
    ("2025-01-09", "Amazon",               -35.76,  "debit",  "Shopping"),
    ("2025-01-08", "GP Prescription",       -9.90,  "debit",  "Healthcare"),
    ("2025-01-07", "Vue Cinema",           -24.00,  "debit",  "Entertainment"),
    ("2025-01-06", "Lidl",                 -43.20,  "debit",  "Groceries"),
    ("2025-01-05", "EE Mobile",            -35.00,  "debit",  "Utilities"),
    ("2025-01-04", "Pret A Manger",         -7.85,  "debit",  "Dining"),
    ("2025-01-03", "Zara",                 -89.99,  "debit",  "Shopping"),
    ("2025-01-02", "National Rail",        -52.40,  "debit",  "Transport"),
    ("2025-01-01", "New Year Bonus",       500.00,  "credit", "Income"),
]


def seed():
    """
    Ensures the schema exists.

    Historically this also inserted a set of global (non-per-user)
    categories, but the schema now requires every category to belong to a
    user (categories.user_id is NOT NULL) — that insert would fail against
    the current schema regardless of which database engine is used. Real
    per-user default categories are created by create_default_categories()
    at registration time instead (see database.py / app.py's register()),
    so this function is kept only for schema initialisation.
    """
    init_db()
    print("Schema ready.")


if __name__ == "__main__":
    seed()
