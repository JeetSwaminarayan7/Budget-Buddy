import os
import io
import re
import json
import datetime
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, create_default_categories

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "budget-buddy-dev-secret-2025")

# In production the frontend (e.g. Vercel) and backend (e.g. Render) live on
# different domains, so the session cookie must be SameSite=None + Secure to
# be sent cross-site. Locally (same-origin via the Vite/nginx proxy) Lax is
# fine and doesn't require HTTPS. Toggle with FLASK_ENV=production.
IS_PRODUCTION = os.environ.get("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_SAMESITE"] = "None" if IS_PRODUCTION else "Lax"
app.config["SESSION_COOKIE_SECURE"]   = IS_PRODUCTION
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 30 * 24 * 60 * 60

# Comma-separated list of allowed frontend origins, e.g.
# "https://budget-buddy.vercel.app,http://localhost:5173"
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]
CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)

init_db()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def uid():
    return session["user_id"]


# ── Auth endpoints ────────────────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = %s OR email = %s", (username, email)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username or email already taken"}), 409

    hashed  = generate_password_hash(password)
    cursor  = conn.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
        (username, email, hashed),
    )
    user_id = cursor.fetchone()[0]
    create_default_categories(user_id, conn)
    conn.commit()
    conn.close()

    session.permanent  = True
    session["user_id"] = user_id
    session["username"] = username
    return jsonify({"id": user_id, "username": username, "email": email}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.permanent   = True
    session["user_id"]  = user["id"]
    session["username"] = user["username"]
    return jsonify({"id": user["id"], "username": user["username"], "email": user["email"]})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, email FROM users WHERE id = %s", (session["user_id"],)
    ).fetchone()
    conn.close()
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 401
    return jsonify(dict(user))


# ── Summary ───────────────────────────────────────────────────────────────────

@app.route("/api/summary", methods=["GET"])
@login_required
def get_summary():
    user_id = uid()
    month   = request.args.get("month", "2025-01")
    conn    = get_db()

    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id=%s AND type='credit' AND date LIKE %s",
        (user_id, f"{month}%")
    ).fetchone()[0]

    total_expenses = conn.execute(
        "SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions WHERE user_id=%s AND type='debit' AND date LIKE %s",
        (user_id, f"{month}%")
    ).fetchone()[0]

    savings      = total_income - total_expenses
    savings_rate = round((savings / total_income * 100), 1) if total_income > 0 else 0

    total_budget = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM budgets WHERE user_id=%s AND month=%s",
        (user_id, month)
    ).fetchone()[0]

    budget_used = round((total_expenses / total_budget * 100), 1) if total_budget > 0 else 0

    conn.close()
    return jsonify({
        "totalIncome":   round(total_income, 2),
        "totalExpenses": round(total_expenses, 2),
        "savings":       round(savings, 2),
        "savingsRate":   savings_rate,
        "budgetUsed":    budget_used,
        "totalBudget":   round(total_budget, 2),
    })


# ── Transactions ──────────────────────────────────────────────────────────────

@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    user_id  = uid()
    month    = request.args.get("month",    "")
    limit    = request.args.get("limit",    200, type=int)
    category = request.args.get("category", "")
    search   = request.args.get("search",   "")
    conn     = get_db()

    conditions = ["t.user_id = %s"]
    params     = [user_id]

    if month:
        conditions.append("t.date LIKE %s")
        params.append(f"{month}%")
    if category:
        conditions.append("c.name = %s")
        params.append(category)
    if search:
        conditions.append("t.description LIKE %s")
        params.append(f"%{search}%")

    params.append(limit)
    where = " AND ".join(conditions)

    rows = conn.execute(
        f"""SELECT t.id, t.date, t.description, t.amount, t.type, t.source,
                  c.name AS category, c.icon, c.color
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           WHERE {where}
           ORDER BY t.date DESC, t.id DESC
           LIMIT %s""",
        params
    ).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/transactions", methods=["POST"])
@login_required
def add_transaction():
    user_id = uid()
    data    = request.get_json()
    conn    = get_db()

    cat = conn.execute(
        "SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, data["category"])
    ).fetchone()
    category_id = cat["id"] if cat else None

    cursor = conn.execute(
        """INSERT INTO transactions (user_id, date, description, amount, type, category_id, source)
           VALUES (%s, %s, %s, %s, %s, %s, 'manual') RETURNING id""",
        (user_id, data["date"], data["description"], data["amount"], data["type"], category_id)
    )
    tx_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({"id": tx_id, "message": "Transaction added"}), 201


@app.route("/api/transactions/<int:tx_id>", methods=["DELETE"])
@login_required
def delete_transaction(tx_id):
    user_id = uid()
    conn    = get_db()
    conn.execute("DELETE FROM transactions WHERE id=%s AND user_id=%s", (tx_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"}), 200


@app.route("/api/transactions/<int:tx_id>", methods=["PATCH"])
@login_required
def update_transaction(tx_id):
    user_id = uid()
    data    = request.get_json()
    conn    = get_db()

    if "category" in data:
        cat = conn.execute(
            "SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, data["category"])
        ).fetchone()
        category_id = cat["id"] if cat else None
        conn.execute(
            "UPDATE transactions SET category_id=%s WHERE id=%s AND user_id=%s",
            (category_id, tx_id, user_id)
        )
        conn.commit()

    conn.close()
    return jsonify({"message": "Updated"}), 200


# ── Categories ────────────────────────────────────────────────────────────────

@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    user_id = uid()
    conn    = get_db()
    rows    = conn.execute(
        "SELECT * FROM categories WHERE user_id=%s ORDER BY name", (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/categories", methods=["POST"])
@login_required
def create_category():
    user_id = uid()
    data    = request.get_json()
    name    = (data.get("name") or "").strip()
    icon    = data.get("icon",  "💳")
    color   = data.get("color", "#6366f1")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    conn     = get_db()
    existing = conn.execute(
        "SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, name)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Category already exists"}), 409

    cursor = conn.execute(
        "INSERT INTO categories (user_id, name, icon, color) VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, name, icon, color)
    )
    cat_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({"id": cat_id, "name": name, "icon": icon, "color": color}), 201


@app.route("/api/categories/<int:cat_id>", methods=["DELETE"])
@login_required
def delete_category(cat_id):
    user_id = uid()
    conn    = get_db()
    cat     = conn.execute(
        "SELECT id FROM categories WHERE id=%s AND user_id=%s", (cat_id, user_id)
    ).fetchone()
    if not cat:
        conn.close()
        return jsonify({"error": "Category not found"}), 404
    conn.execute("DELETE FROM categories WHERE id=%s AND user_id=%s", (cat_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Category deleted"}), 200


# ── Category Breakdown ────────────────────────────────────────────────────────

@app.route("/api/breakdown", methods=["GET"])
@login_required
def get_breakdown():
    user_id = uid()
    month   = request.args.get("month", "2025-01")
    conn    = get_db()

    rows = conn.execute(
        """SELECT c.name, c.icon, c.color,
                  COALESCE(SUM(ABS(t.amount)), 0) AS value
           FROM categories c
           LEFT JOIN transactions t
             ON t.category_id = c.id
             AND t.type = 'debit'
             AND t.date LIKE %s
             AND t.user_id = %s
           WHERE c.user_id = %s AND c.name != 'Income'
           GROUP BY c.id, c.name, c.icon, c.color
           ORDER BY value DESC""",
        (f"{month}%", user_id, user_id)
    ).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


# ── Monthly Trend ─────────────────────────────────────────────────────────────

@app.route("/api/trend", methods=["GET"])
@login_required
def get_trend():
    user_id = uid()
    conn    = get_db()

    rows = conn.execute(
        """SELECT
             LEFT(date, 7) AS month,
             COALESCE(SUM(CASE WHEN type='credit' THEN amount ELSE 0 END), 0) AS income,
             COALESCE(SUM(CASE WHEN type='debit'  THEN ABS(amount) ELSE 0 END), 0) AS expenses
           FROM transactions
           WHERE user_id = %s
           GROUP BY LEFT(date, 7)
           ORDER BY month ASC
           LIMIT 6""",
        (user_id,)
    ).fetchall()

    result = []
    for r in rows:
        d = datetime.datetime.strptime(r["month"], "%Y-%m")
        result.append({
            "month":    d.strftime("%b"),
            "income":   round(r["income"], 2),
            "expenses": round(r["expenses"], 2),
        })

    conn.close()
    return jsonify(result)


# ── Budgets ───────────────────────────────────────────────────────────────────

@app.route("/api/budgets", methods=["GET"])
@login_required
def get_budgets():
    user_id = uid()
    month   = request.args.get("month", "2025-01")
    conn    = get_db()

    # Return ALL user categories with their budget (0 if not set)
    rows = conn.execute(
        """SELECT c.id, c.name, c.icon, c.color,
                  COALESCE(MAX(b.amount), 0) AS budget,
                  COALESCE(SUM(ABS(t.amount)), 0) AS spent
           FROM categories c
           LEFT JOIN budgets b
             ON b.category_id = c.id AND b.user_id = %s AND b.month = %s
           LEFT JOIN transactions t
             ON t.category_id = c.id
             AND t.type = 'debit'
             AND t.date LIKE %s
             AND t.user_id = %s
           WHERE c.user_id = %s AND c.name != 'Income'
           GROUP BY c.id, c.name, c.icon, c.color
           ORDER BY spent DESC""",
        (user_id, month, f"{month}%", user_id, user_id)
    ).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/budgets", methods=["PUT"])
@login_required
def update_budget():
    user_id       = uid()
    data          = request.get_json()
    category_name = data.get("category")
    amount        = data.get("amount")
    month         = data.get("month", "2025-01")

    if not category_name or amount is None:
        return jsonify({"error": "category and amount are required"}), 400

    conn = get_db()
    cat  = conn.execute(
        "SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, category_name)
    ).fetchone()
    if not cat:
        conn.close()
        return jsonify({"error": f"Category '{category_name}' not found"}), 404

    conn.execute(
        """INSERT INTO budgets (user_id, category_id, amount, month) VALUES (%s, %s, %s, %s)
           ON CONFLICT(user_id, category_id, month) DO UPDATE SET amount = excluded.amount""",
        (user_id, cat["id"], float(amount), month)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Budget updated"}), 200


# ── Monthly Budget (total) ────────────────────────────────────────────────────

@app.route("/api/budget/monthly", methods=["GET"])
@login_required
def get_monthly_budget():
    user_id = uid()
    conn    = get_db()
    row     = conn.execute(
        "SELECT monthly_budget FROM users WHERE id=%s", (user_id,)
    ).fetchone()
    conn.close()
    return jsonify({"amount": round(row["monthly_budget"], 2) if row else 1000})


@app.route("/api/budget/monthly", methods=["PUT"])
@login_required
def update_monthly_budget():
    user_id = uid()
    data    = request.get_json()
    amount  = data.get("amount")

    if amount is None:
        return jsonify({"error": "amount is required"}), 400

    conn = get_db()
    conn.execute(
        "UPDATE users SET monthly_budget=%s WHERE id=%s", (float(amount), user_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Monthly budget updated"}), 200


# ── User Settings (monthly budget + savings goal) ─────────────────────────────

@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    user_id = uid()
    conn    = get_db()
    row     = conn.execute(
        "SELECT monthly_budget, savings_goal FROM users WHERE id=%s", (user_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        "monthly_budget": round(row["monthly_budget"], 2) if row else 1000,
        "savings_goal":   round(row["savings_goal"],   2) if row else 500,
    })


@app.route("/api/settings", methods=["PUT"])
@login_required
def update_settings():
    user_id        = uid()
    data           = request.get_json()
    monthly_budget = data.get("monthly_budget")
    savings_goal   = data.get("savings_goal")

    if monthly_budget is None and savings_goal is None:
        return jsonify({"error": "No fields to update"}), 400

    conn = get_db()
    if monthly_budget is not None:
        conn.execute("UPDATE users SET monthly_budget=%s WHERE id=%s", (float(monthly_budget), user_id))
    if savings_goal is not None:
        conn.execute("UPDATE users SET savings_goal=%s WHERE id=%s", (float(savings_goal), user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Settings updated"}), 200


# ── Upload: Extract ───────────────────────────────────────────────────────────

@app.route("/api/upload", methods=["POST"])
@login_required
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not configured — add it to backend/.env"}), 500

    try:
        import pdfplumber
        pdf_bytes = file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return jsonify({"error": "Could not extract text from this PDF. It may be scanned or image-based."}), 400

    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 400

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        prompt = (
            "Extract all bank transactions from the following bank statement text.\n"
            "Return ONLY a valid JSON array with no explanation, no markdown, no code fences.\n"
            "Each object must have exactly these fields:\n"
            '  "date": string in YYYY-MM-DD format\n'
            '  "description": string (merchant or payee name, concise)\n'
            '  "amount": number (always positive)\n'
            '  "type": "debit" for money out, "credit" for money in\n\n'
            f"Bank statement text:\n{text}\n\n"
            "JSON array:"
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()

        transactions = json.loads(content)
        if not isinstance(transactions, list):
            raise ValueError("Expected a JSON array")

        return jsonify({"transactions": transactions})

    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid JSON. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": f"AI processing failed: {str(e)}"}), 500


# ── Upload: Confirm & Save ────────────────────────────────────────────────────

@app.route("/api/upload/confirm", methods=["POST"])
@login_required
def confirm_upload():
    user_id      = uid()
    data         = request.get_json()
    transactions = data.get("transactions", [])

    if not transactions:
        return jsonify({"error": "No transactions to save"}), 400

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY not configured — add it to backend/.env"}), 500

    conn      = get_db()
    user_cats = conn.execute(
        "SELECT id, name FROM categories WHERE user_id=%s", (user_id,)
    ).fetchall()
    cat_map            = {r["name"]: r["id"] for r in user_cats}
    upload_categories  = list(cat_map.keys())

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        numbered = "\n".join(
            f"{i + 1}. {tx['description']} ({tx['type']})"
            for i, tx in enumerate(transactions)
        )
        cat_prompt = (
            f"Categorise each bank transaction below into exactly one category from this list: "
            f"{', '.join(upload_categories)}.\n\n"
            f"{numbered}\n\n"
            "Reply with ONLY a JSON array of category name strings in the same order as the transactions. "
            'Example: ["Groceries","Transport","Income"]\n'
            "JSON array:"
        )

        cat_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": cat_prompt}],
            temperature=0,
        )
        cat_content = cat_response.choices[0].message.content.strip()
        cat_content = re.sub(r"^```(?:json)?\s*", "", cat_content)
        cat_content = re.sub(r"\s*```$", "", cat_content).strip()

        try:
            category_names = json.loads(cat_content)
        except json.JSONDecodeError:
            category_names = [
                "Income" if tx["type"] == "credit" else "Shopping"
                for tx in transactions
            ]

        saved = 0
        for i, tx in enumerate(transactions):
            cat_name = category_names[i] if i < len(category_names) else None
            if not cat_name or cat_name not in cat_map:
                cat_name = "Income" if tx["type"] == "credit" else "Shopping"
            category_id = cat_map.get(cat_name)

            conn.execute(
                """INSERT INTO transactions (user_id, date, description, amount, type, category_id, source)
                   VALUES (%s, %s, %s, %s, %s, %s, 'pdf')""",
                (user_id, tx["date"], tx["description"], float(tx["amount"]), tx["type"], category_id),
            )
            saved += 1

        conn.commit()

        DEFAULT_BUDGETS = [
            ("Housing", 900), ("Groceries", 300), ("Transport", 200),
            ("Dining", 200), ("Entertainment", 100), ("Utilities", 180),
            ("Healthcare", 80), ("Shopping", 150),
        ]
        uploaded_months = {tx["date"][:7] for tx in transactions if "date" in tx}
        for month in uploaded_months:
            existing = conn.execute(
                "SELECT COUNT(*) FROM budgets WHERE user_id=%s AND month=%s", (user_id, month)
            ).fetchone()[0]
            if existing == 0:
                for cat_name, amount in DEFAULT_BUDGETS:
                    cat_id = cat_map.get(cat_name)
                    if cat_id:
                        conn.execute(
                            """INSERT INTO budgets (user_id, category_id, amount, month)
                               VALUES (%s, %s, %s, %s)
                               ON CONFLICT (user_id, category_id, month) DO NOTHING""",
                            (user_id, cat_id, amount, month)
                        )
        conn.commit()
        conn.close()
        return jsonify({
            "saved": saved,
            "message": f"{saved} transaction{'s' if saved != 1 else ''} saved",
        })

    except Exception as e:
        conn.close()
        return jsonify({"error": f"Failed to save transactions: {str(e)}"}), 500


# ── Months ────────────────────────────────────────────────────────────────────

@app.route("/api/months", methods=["GET"])
@login_required
def get_months():
    user_id = uid()
    conn    = get_db()
    rows    = conn.execute(
        """SELECT DISTINCT LEFT(date, 7) AS month
           FROM transactions
           WHERE user_id = %s
           ORDER BY month DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([r["month"] for r in rows])


# ── Health check ──────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Budget Buddy API running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
