import { useState, useEffect, type FormEvent } from "react";
import { fetchBudgets, fetchMonths, updateBudget, fetchMonthlyBudget, updateMonthlyBudget, createCategory } from "./api";
import type { Budget } from "./types";

const ICON_OPTIONS = ["🛒","🚌","🍽️","🎬","💡","🏠","🏥","🛍️","📚","✈️","🎮","💻","👗","🐾","🎵","🏋️","📱","🍕","☕","🎁","💈","🔧","📦","🌱"];

interface CategoryRowProps {
  budget: Budget;
  month: string | null;
  onSave: (name: string, amount: number) => Promise<void>;
}

function CategoryRow({ budget, onSave }: CategoryRowProps) {
  const [value, setValue] = useState(String(budget.budget === 0 ? "" : budget.budget));
  const [saving, setSaving] = useState(false);

  const pct      = budget.budget > 0 ? Math.min(Math.round((budget.spent / budget.budget) * 100), 100) : 0;
  const isOver   = budget.spent > budget.budget && budget.budget > 0;
  const barColor = isOver ? "var(--red)" : pct > 75 ? "var(--amber)" : "var(--indigo)";

  async function save() {
    const num = parseFloat(value);
    if (isNaN(num) || num < 0 || num === budget.budget) return;
    setSaving(true);
    await onSave(budget.name, num);
    setSaving(false);
  }

  return (
    <div className="bcat-row">
      <div className="bcat-row-top">
        <span className="bcat-row-name">{budget.icon} {budget.name}</span>
        <span className="bcat-row-amounts" style={{ color: isOver ? "var(--red)" : "var(--text-muted)" }}>
          £{budget.spent.toFixed(2)}
          <span style={{ color: "var(--text-dim)" }}> / </span>
          £{budget.budget > 0 ? budget.budget.toFixed(2) : "—"}
        </span>
      </div>
      <div className="bcat-row-controls">
        <div className="bcat-input-wrap">
          <span className="bcat-input-prefix">£</span>
          <input
            className="bcat-input"
            type="number"
            min="0"
            placeholder="0"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={save}
            onKeyDown={(e) => e.key === "Enter" && save()}
            disabled={saving}
          />
        </div>
        <div className="bcat-bar-track">
          <div className="bcat-bar-fill" style={{ width: `${pct}%`, background: barColor }} />
        </div>
        {budget.budget > 0 && (
          <span className="bcat-pct" style={{ color: barColor }}>{pct}%</span>
        )}
      </div>
    </div>
  );
}

interface NewCategoryForm {
  name: string;
  icon: string;
  color: string;
}

export default function Budgets() {
  const [budgets, setBudgets]             = useState<Budget[]>([]);
  const [month, setMonth]                 = useState<string | null>(null);
  const [monthLabel, setMonthLabel]       = useState("");
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState<string | null>(null);
  const [monthlyBudget, setMonthlyBudget] = useState(0);
  const [monthlyInput, setMonthlyInput]   = useState("");
  const [monthlySaving, setMonthlySaving] = useState(false);
  const [monthlySaved, setMonthlySaved]   = useState(false);
  const [showAddForm, setShowAddForm]     = useState(false);
  const [newCat, setNewCat]               = useState<NewCategoryForm>({ name: "", icon: "💳", color: "#6366f1" });
  const [addSaving, setAddSaving]         = useState(false);
  const [addError, setAddError]           = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const months = await fetchMonths();
        const m = months[0] ?? new Date().toISOString().slice(0, 7);
        setMonth(m);
        setMonthLabel(new Date(m + "-01").toLocaleString("en-GB", { month: "long", year: "numeric" }));
        const [data, mb] = await Promise.all([fetchBudgets(m), fetchMonthlyBudget()]);
        setBudgets(data);
        setMonthlyBudget(mb.amount ?? 0);
        setMonthlyInput(mb.amount > 0 ? String(mb.amount) : "");
      } catch {
        setError("Failed to load budgets. Is the backend running?");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleCatSave(catName: string, newAmount: number) {
    setBudgets((prev) => prev.map((b) => b.name === catName ? { ...b, budget: newAmount } : b));
    if (!month) return;
    await updateBudget({ category: catName, amount: newAmount, month });
  }

  async function handleMonthlySave(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const num = parseFloat(monthlyInput);
    if (isNaN(num) || num < 0) return;
    setMonthlySaving(true);
    await updateMonthlyBudget({ amount: num });
    setMonthlyBudget(num);
    setMonthlySaving(false);
    setMonthlySaved(true);
    setTimeout(() => setMonthlySaved(false), 2000);
  }

  async function handleAddCategory(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setAddError(null);
    const name = newCat.name.trim();
    if (!name) { setAddError("Category name is required"); return; }
    setAddSaving(true);
    try {
      const res = await createCategory({ name, icon: newCat.icon, color: newCat.color });
      if ("error" in res) { setAddError(res.error); return; }
      if (month) {
        const data = await fetchBudgets(month);
        setBudgets(data);
      }
      setNewCat({ name: "", icon: "💳", color: "#6366f1" });
      setShowAddForm(false);
    } catch {
      setAddError("Failed to create category.");
    } finally {
      setAddSaving(false);
    }
  }

  if (loading) return <main className="main-content"><div className="loading-state">Loading budgets…</div></main>;
  if (error)   return <main className="main-content"><div className="upload-message upload-message-error"><span>⚠</span> {error}</div></main>;

  const totalSpent    = budgets.reduce((s, b) => s + b.spent, 0);
  const budgetSet     = monthlyBudget > 0 ? monthlyBudget : budgets.reduce((s, b) => s + b.budget, 0);
  const remaining     = budgetSet - totalSpent;
  const progressPct   = budgetSet > 0 ? Math.min(Math.round((totalSpent / budgetSet) * 100), 100) : 0;
  const barColor      = progressPct > 90 ? "var(--red)" : progressPct > 70 ? "var(--amber)" : "var(--indigo)";
  const overCount     = budgets.filter((b) => b.spent > b.budget && b.budget > 0).length;

  return (
    <main className="main-content">
      <div className="page-header">
        <h1 className="page-title">Budget</h1>
        <p className="page-subtitle">Manage your spending limits for {monthLabel}</p>
      </div>

      {/* Monthly Budget Overview */}
      <div className="chart-card" style={{ marginBottom: 20 }}>
        <h2 className="chart-title" style={{ marginBottom: 4 }}>Monthly Budget Overview</h2>
        <p className="chart-subtitle" style={{ marginBottom: 20 }}>Track your overall spending for {monthLabel}</p>

        <div className="bov-stats">
          <div className="bov-stat bov-stat-blue">
            <span className="bov-stat-label">Budget Set</span>
            <span className="bov-stat-value">£{budgetSet.toFixed(2)}</span>
          </div>
          <div className="bov-stat bov-stat-red">
            <span className="bov-stat-label">Spent</span>
            <span className="bov-stat-value" style={{ color: "var(--red)" }}>£{totalSpent.toFixed(2)}</span>
          </div>
          <div className="bov-stat bov-stat-green">
            <span className="bov-stat-label">Remaining</span>
            <span className="bov-stat-value" style={{ color: remaining < 0 ? "var(--red)" : "var(--green)" }}>
              £{Math.abs(remaining).toFixed(2)}{remaining < 0 ? " over" : ""}
            </span>
          </div>
        </div>

        <div style={{ marginTop: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: "var(--text)" }}>Budget Progress</span>
            <span style={{ fontSize: 14, fontWeight: 700, color: barColor }}>{progressPct}%</span>
          </div>
          <div className="budget-track">
            <div className="budget-fill" style={{ width: `${progressPct}%`, background: barColor }} />
          </div>
        </div>

        {overCount > 0 && (
          <div className="budget-over-banner" style={{ marginTop: 16, marginBottom: 0 }}>
            ⚠ {overCount} {overCount === 1 ? "category is" : "categories are"} over budget this month.
          </div>
        )}
      </div>

      {/* Set Monthly Budget */}
      <div className="chart-card" style={{ marginBottom: 20 }}>
        <h2 className="chart-title" style={{ marginBottom: 4 }}>Set Monthly Budget</h2>
        <p className="chart-subtitle" style={{ marginBottom: 20 }}>Define your total spending limit for the month</p>

        <form className="bset-form" onSubmit={handleMonthlySave}>
          <div className="bset-field">
            <label className="bset-label">Monthly Budget Amount</label>
            <div className="bset-input-wrap">
              <span className="bset-prefix">£</span>
              <input
                className="bset-input"
                type="number"
                min="0"
                step="any"
                placeholder="e.g. 800"
                value={monthlyInput}
                onChange={(e) => setMonthlyInput(e.target.value)}
              />
            </div>
            <p className="bset-hint">Recommended budget for students: £600–£1000/month</p>
          </div>
          <button className="budget-save-btn" type="submit" disabled={monthlySaving} style={{ alignSelf: "flex-start" }}>
            {monthlySaving ? "Saving…" : monthlySaved ? "Saved ✓" : "Save Budget"}
          </button>
        </form>
      </div>

      {/* Category Budgets */}
      <div className="chart-card">
        <div className="budget-section-header" style={{ marginBottom: 20 }}>
          <div>
            <h2 className="chart-title" style={{ marginBottom: 4 }}>Category Budgets</h2>
            <p className="chart-subtitle">Set spending limits for specific categories</p>
          </div>
          <button className="budget-add-toggle-btn" onClick={() => setShowAddForm((v) => !v)}>
            {showAddForm ? "✕ Cancel" : "+ Add Category"}
          </button>
        </div>

        {showAddForm && (
          <div className="budget-add-section" style={{ marginBottom: 20 }}>
            <div className="budget-add-title">New Category</div>
            {addError && (
              <div className="upload-message upload-message-error" style={{ marginBottom: 12 }}>{addError}</div>
            )}
            <form className="budget-add-form" onSubmit={handleAddCategory}>
              <div className="budget-add-field">
                <label className="budget-add-label">Name</label>
                <input
                  className="budget-add-input"
                  placeholder="e.g. Subscriptions"
                  value={newCat.name}
                  onChange={(e) => setNewCat((c) => ({ ...c, name: e.target.value }))}
                  style={{ width: 180 }}
                  required
                />
              </div>
              <div className="budget-add-field">
                <label className="budget-add-label">Icon</label>
                <select
                  className="budget-add-input"
                  value={newCat.icon}
                  onChange={(e) => setNewCat((c) => ({ ...c, icon: e.target.value }))}
                  style={{ width: 80 }}
                >
                  {ICON_OPTIONS.map((ic) => <option key={ic} value={ic}>{ic}</option>)}
                </select>
              </div>
              <div className="budget-add-field">
                <label className="budget-add-label">Colour</label>
                <input
                  type="color"
                  className="budget-add-input"
                  value={newCat.color}
                  onChange={(e) => setNewCat((c) => ({ ...c, color: e.target.value }))}
                  style={{ width: 56, padding: "4px 6px", height: 38, cursor: "pointer" }}
                />
              </div>
              <button className="budget-add-btn" type="submit" disabled={addSaving}>
                {addSaving ? "Adding…" : "Add"}
              </button>
            </form>
          </div>
        )}

        <div className="bcat-list">
          {budgets.map((b) => (
            <CategoryRow key={b.name} budget={b} month={month} onSave={handleCatSave} />
          ))}
        </div>
      </div>
    </main>
  );
}
