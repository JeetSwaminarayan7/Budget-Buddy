import { useState, useEffect, useRef } from "react";
import { useAuth } from "./context/AuthContext";
import SummaryCards from "./components/SummaryCards";
import SpendingChart from "./components/SpendingChart";
import TrendChart from "./components/TrendChart";
import IncomeExpenseChart from "./components/IncomeExpenseChart";
import RecentTransactions from "./components/RecentTransactions";
import {
  fetchSummary, fetchBreakdown, fetchTrend, fetchTransactions,
  fetchBudgets, fetchMonths, fetchSettings, updateSettings,
} from "./api";

function InlineEdit({ value, onSave, prefix = "£" }) {
  const [editing, setEditing] = useState(false);
  const [draft,   setDraft]   = useState("");
  const inputRef = useRef(null);

  function start() {
    setDraft(String(value));
    setEditing(true);
    setTimeout(() => inputRef.current?.select(), 0);
  }

  function commit() {
    const n = parseFloat(draft);
    if (!isNaN(n) && n > 0) onSave(n);
    setEditing(false);
  }

  if (editing) {
    return (
      <input
        ref={inputRef}
        className="inline-edit-input"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => { if (e.key === "Enter") commit(); if (e.key === "Escape") setEditing(false); }}
      />
    );
  }

  return (
    <span className="inline-edit-trigger" onClick={start} title="Click to edit">
      {prefix}{Number(value).toLocaleString()} ✎
    </span>
  );
}

export default function Dashboard() {
  const { user }                          = useAuth();
  const [summary, setSummary]             = useState(null);
  const [breakdown, setBreakdown]         = useState([]);
  const [trend, setTrend]                 = useState([]);
  const [transactions, setTransactions]   = useState([]);
  const [budgets, setBudgets]             = useState([]);
  const [settings, setSettings]           = useState({ monthly_budget: 1000, savings_goal: 500 });
  const [loading, setLoading]             = useState(true);
  const [month, setMonth]                 = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [months, cfg] = await Promise.all([fetchMonths(), fetchSettings()]);
        const m = months[0] ?? new Date().toISOString().slice(0, 7);
        setMonth(m);
        setSettings(cfg);

        const [s, b, tr, tx, bud] = await Promise.all([
          fetchSummary(m),
          fetchBreakdown(m),
          fetchTrend(),
          fetchTransactions({ month: m, limit: 10 }),
          fetchBudgets(m),
        ]);
        setSummary(s);
        setBreakdown(b);
        setTrend(tr);
        setTransactions(tx);
        setBudgets(bud);
      } catch (err) {
        console.error("Dashboard load failed:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function saveMonthlyBudget(n) {
    setSettings((s) => ({ ...s, monthly_budget: n }));
    await updateSettings({ monthly_budget: n });
  }

  async function saveSavingsGoal(n) {
    setSettings((s) => ({ ...s, savings_goal: n }));
    await updateSettings({ savings_goal: n });
  }

  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-state">Loading dashboard…</div>
      </main>
    );
  }

  const firstName  = user?.username?.split(" ")[0] ?? "there";
  const monthLabel = month
    ? new Date(month + "-01").toLocaleString("en-GB", { month: "long", year: "numeric" })
    : "";

  const totalExpenses  = summary?.totalExpenses ?? 0;
  const monthlyBudget  = settings.monthly_budget;
  const savingsGoal    = settings.savings_goal;

  const budgetPct  = monthlyBudget > 0 ? Math.round((totalExpenses / monthlyBudget) * 100) : 0;
  const savings    = summary?.savings ?? 0;
  const savingsPct = Math.min(Math.round((savings / savingsGoal) * 100), 100);
  const onTrack    = savings >= savingsGoal * 0.8;
  const overspent  = budgets.filter((b) => b.spent > b.budget && b.budget > 0);

  return (
    <main className="main-content">
      {/* Overspend alerts */}
      {overspent.length > 0 && (
        <div className="alerts-strip">
          {overspent.map((b) => (
            <div className="alert-item" key={b.name}>
              <span>⚠</span>
              <span>
                {b.icon} <strong>{b.name}</strong> over budget — spent{" "}
                <strong>£{b.spent.toFixed(2)}</strong> of £{b.budget.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Page header */}
      <div className="page-header">
        <h1 className="page-title">Welcome back, {firstName}! 👋</h1>
        <p className="page-subtitle">Here's your financial overview for {monthLabel}</p>
      </div>

      {/* Summary cards */}
      <SummaryCards summary={summary} monthlyBudget={monthlyBudget} />

      {/* Two charts side by side */}
      <div className="charts-grid">
        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-card-header">
            <div>
              <h2 className="chart-title">Spending by Category</h2>
              <p className="chart-subtitle">Breakdown of your expenses</p>
            </div>
          </div>
          <SpendingChart data={breakdown} />
        </div>

        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-card-header">
            <div>
              <h2 className="chart-title">Income vs Expenses</h2>
              <p className="chart-subtitle">Compare spending across categories</p>
            </div>
            <div className="chart-legend-inline">
              <span className="legend-pill" style={{ background: "var(--green-subtle)", color: "var(--green)" }}>● Income</span>
              <span className="legend-pill" style={{ background: "var(--red-subtle)", color: "var(--red)" }}>● Expenses</span>
            </div>
          </div>
          <IncomeExpenseChart breakdown={breakdown} income={summary?.totalIncome ?? 0} />
        </div>
      </div>

      {/* Budget + Savings row */}
      <div className="dashboard-bottom-row">
        <div className="budget-bar-section">
          <div className="budget-bar-header">
            <span className="budget-bar-label">Monthly Budget Used</span>
            <span className="budget-bar-value">
              {budgetPct}% of{" "}
              <InlineEdit value={monthlyBudget} onSave={saveMonthlyBudget} />
            </span>
          </div>
          <div className="budget-track">
            <div
              className="budget-fill"
              style={{
                width: `${Math.min(budgetPct, 100)}%`,
                background: budgetPct > 90 ? "var(--red)" : budgetPct > 70 ? "var(--amber)" : "var(--green)",
              }}
            />
          </div>
          <span className="budget-bar-hint">£{totalExpenses.toFixed(2)} spent · click amount to edit</span>
        </div>

        <div className="savings-goal-card">
          <div className="savings-goal-header">
            <span className="savings-goal-title">Monthly Savings Goal</span>
            <span
              className="savings-goal-badge"
              style={{
                background: onTrack ? "var(--green-subtle)" : "var(--amber-subtle)",
                color:      onTrack ? "var(--green)"        : "var(--amber)",
              }}
            >
              {onTrack ? "On Track" : "Behind"}
            </span>
          </div>
          <div className="savings-goal-nums">
            <span className="savings-actual">£{savings.toFixed(2)}</span>
            <span className="savings-target"> / <InlineEdit value={savingsGoal} onSave={saveSavingsGoal} /> goal</span>
          </div>
          <div className="budget-track">
            <div
              className="budget-fill"
              style={{ width: `${savingsPct}%`, background: onTrack ? "var(--green)" : "var(--amber)" }}
            />
          </div>
          <span className="savings-pct">{savingsPct}% achieved · click goal to edit</span>
        </div>
      </div>

      {/* Spending trends line chart */}
      <div className="chart-card">
        <div className="chart-card-header">
          <div>
            <h2 className="chart-title">Spending Trends</h2>
            <p className="chart-subtitle">Track your income and expenses over time</p>
          </div>
          <div className="chart-legend-inline">
            <span className="legend-pill" style={{ background: "var(--green-subtle)", color: "var(--green)" }}>— Income</span>
            <span className="legend-pill" style={{ background: "var(--red-subtle)", color: "var(--red)" }}>- - Expenses</span>
          </div>
        </div>
        <TrendChart data={trend} />
      </div>

      {/* Recent transactions */}
      <div className="chart-card" style={{ marginBottom: 0 }}>
        <div className="chart-card-header">
          <div>
            <h2 className="chart-title">Recent Transactions</h2>
            <p className="chart-subtitle">Review and categorize your transactions</p>
          </div>
        </div>
        <RecentTransactions transactions={transactions} />
      </div>
    </main>
  );
}
