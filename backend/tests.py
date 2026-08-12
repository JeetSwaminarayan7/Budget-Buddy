"""
Budget Buddy — Backend Unit Tests
Run:  python -m pytest tests.py -v
  or: python tests.py

Requires a PostgreSQL instance reachable via the DATABASE_URL env var
(defaults to a local test database — see database.py). CI provisions a
throwaway PostgreSQL service container for this; see .github/workflows/ci.yml.
"""

import json
import os
import sys
import unittest

# Point at a dedicated test database if one isn't already set via env var.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:testpass@localhost:5432/budget_buddy_test",
)

import database  # noqa: E402 — must come after DATABASE_URL is set
from database import init_db, get_db  # noqa: E402
from seed import seed          # noqa: E402
from app import app            # noqa: E402


def _reset_schema():
    """
    Unlike the old SQLite setup (a fresh temp file every run), a Postgres
    test database persists between runs, so we drop all tables first to
    guarantee a clean slate and avoid unique-constraint clashes from a
    previous run's leftover data.
    """
    conn = get_db()
    conn.execute(
        "DROP TABLE IF EXISTS budgets, monthly_budgets, transactions, categories, users CASCADE"
    )
    conn.commit()
    conn.close()


class BudgetBuddyAPITests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _reset_schema()
        init_db()
        seed()
        app.config["TESTING"] = True
        cls.client = app.test_client()

        # Register + log in a test user. The Flask test client persists
        # cookies across requests on the same client instance, so every
        # subsequent call in this suite is authenticated automatically.
        cls.client.post(
            "/api/auth/register",
            data=json.dumps({
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpass123",
            }),
            content_type="application/json",
        )

        # `seed()` only creates default categories for a new user — it does not
        # create any transactions. Seed a handful directly through the API so
        # summary/transactions/breakdown/trend endpoints have real data to
        # operate on, matching the default category names in database.py.
        SEED_TRANSACTIONS = [
            ("2025-01-24", "Tesco Superstore",  -87.43,  "debit",  "Groceries"),
            ("2025-01-24", "Salary - January", 3850.00,  "credit", "Income"),
            ("2025-01-23", "Netflix",           -17.99,  "debit",  "Entertainment"),
            ("2025-01-21", "Nando's Watford",   -32.50,  "debit",  "Dining"),
            ("2025-01-17", "Rent - January",   -850.00,  "debit",  "Housing"),
        ]
        for date, description, amount, tx_type, category in SEED_TRANSACTIONS:
            cls.client.post(
                "/api/transactions",
                data=json.dumps({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "type": tx_type,
                    "category": category,
                }),
                content_type="application/json",
            )

    @classmethod
    def tearDownClass(cls):
        _reset_schema()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def get(self, url):
        return self.client.get(url)

    def post(self, url, body):
        return self.client.post(
            url,
            data=json.dumps(body),
            content_type="application/json",
        )

    def put(self, url, body):
        return self.client.put(
            url,
            data=json.dumps(body),
            content_type="application/json",
        )

    def patch(self, url, body):
        return self.client.patch(
            url,
            data=json.dumps(body),
            content_type="application/json",
        )

    def delete(self, url):
        return self.client.delete(url)

    def json(self, res):
        return json.loads(res.data)

    # ── Health ───────────────────────────────────────────────────────────────

    def test_01_health(self):
        res = self.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertEqual(data["status"], "ok")

    # ── Summary ──────────────────────────────────────────────────────────────

    def test_02_summary_returns_expected_fields(self):
        res = self.get("/api/summary?month=2025-01")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        for field in ("totalIncome", "totalExpenses", "savings", "savingsRate", "budgetUsed"):
            self.assertIn(field, data, f"Missing field: {field}")

    def test_03_summary_income_positive(self):
        res = self.get("/api/summary?month=2025-01")
        data = self.json(res)
        self.assertGreater(data["totalIncome"], 0)

    def test_04_summary_expenses_positive(self):
        res = self.get("/api/summary?month=2025-01")
        data = self.json(res)
        self.assertGreater(data["totalExpenses"], 0)

    # ── Categories ───────────────────────────────────────────────────────────

    def test_05_categories_returns_list(self):
        res = self.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_06_categories_have_required_fields(self):
        res = self.get("/api/categories")
        data = self.json(res)
        for field in ("id", "name", "icon", "color"):
            self.assertIn(field, data[0], f"Missing field: {field}")

    # ── Transactions ─────────────────────────────────────────────────────────

    def test_07_transactions_list(self):
        res = self.get("/api/transactions?month=2025-01&limit=5")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)

    def test_08_transactions_no_filter_returns_all(self):
        res = self.get("/api/transactions?limit=200")
        data = self.json(res)
        self.assertGreater(len(data), 0)

    def test_09_transactions_search_filter(self):
        res = self.get("/api/transactions?search=Tesco")
        data = self.json(res)
        self.assertTrue(
            all("Tesco" in tx["description"] for tx in data),
            "Search filter returned non-matching rows",
        )

    def test_10_transactions_category_filter(self):
        res = self.get("/api/transactions?month=2025-01&category=Groceries")
        data = self.json(res)
        self.assertTrue(
            all(tx["category"] == "Groceries" for tx in data),
            "Category filter returned wrong categories",
        )

    def test_11_add_and_delete_transaction(self):
        payload = {
            "date": "2025-01-30",
            "description": "Test Shop",
            "amount": 19.99,
            "type": "debit",
            "category": "Shopping",
        }
        res = self.post("/api/transactions", payload)
        self.assertEqual(res.status_code, 201)
        tx_id = self.json(res)["id"]
        self.assertIsInstance(tx_id, int)

        res = self.delete(f"/api/transactions/{tx_id}")
        self.assertEqual(res.status_code, 200)

    def test_12_patch_transaction_category(self):
        res = self.get("/api/transactions?month=2025-01&limit=1")
        tx  = self.json(res)[0]
        tx_id = tx["id"]

        res = self.patch(f"/api/transactions/{tx_id}", {"category": "Dining"})
        self.assertEqual(res.status_code, 200)

        # Verify it was changed
        res = self.get(f"/api/transactions?month=2025-01&search={tx['description']}")
        updated = next((t for t in self.json(res) if t["id"] == tx_id), None)
        if updated:
            self.assertEqual(updated["category"], "Dining")

    # ── Breakdown ────────────────────────────────────────────────────────────

    def test_13_breakdown_returns_list(self):
        res = self.get("/api/breakdown?month=2025-01")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)

    def test_14_breakdown_has_value_field(self):
        res = self.get("/api/breakdown?month=2025-01")
        data = self.json(res)
        for row in data:
            self.assertIn("value", row)
            self.assertGreaterEqual(row["value"], 0)

    # ── Trend ────────────────────────────────────────────────────────────────

    def test_15_trend_returns_months(self):
        res = self.get("/api/trend")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("month",    data[0])
            self.assertIn("income",   data[0])
            self.assertIn("expenses", data[0])

    # ── Budgets ──────────────────────────────────────────────────────────────

    def test_16_budgets_returns_list(self):
        res = self.get("/api/budgets?month=2025-01")
        self.assertEqual(res.status_code, 200)
        data = self.json(res)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_17_budgets_have_spent_and_budget(self):
        res = self.get("/api/budgets?month=2025-01")
        data = self.json(res)
        for row in data:
            self.assertIn("budget", row)
            self.assertIn("spent",  row)

    def test_18_put_budget_updates_amount(self):
        res = self.put(
            "/api/budgets",
            {"category": "Groceries", "amount": 450.00, "month": "2025-01"},
        )
        self.assertEqual(res.status_code, 200)

        # Verify the change
        res   = self.get("/api/budgets?month=2025-01")
        groc  = next((b for b in self.json(res) if b["name"] == "Groceries"), None)
        self.assertIsNotNone(groc)
        self.assertAlmostEqual(groc["budget"], 450.00, places=2)

    def test_19_put_budget_bad_category(self):
        res = self.put(
            "/api/budgets",
            {"category": "NonExistent", "amount": 100.00, "month": "2025-01"},
        )
        self.assertEqual(res.status_code, 404)

    def test_20_put_budget_missing_fields(self):
        res = self.put("/api/budgets", {"amount": 100.00})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
