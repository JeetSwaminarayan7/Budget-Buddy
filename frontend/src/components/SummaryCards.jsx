const fmt = (n) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" }).format(n ?? 0);

export default function SummaryCards({ summary, monthlyBudget = 1000 }) {
  const totalExpenses = summary?.totalExpenses ?? 0;
  const budgetUsed    = monthlyBudget > 0 ? Math.round((totalExpenses / monthlyBudget) * 100) : 0;
  const remaining     = monthlyBudget - totalExpenses;

  return (
    <div className="summary-grid">
      {/* Total Income */}
      <div className="summary-card summary-card-income">
        <div className="card-icon-row">
          <span className="card-label">Total Income</span>
          <span className="card-icon-wrap">↑</span>
        </div>
        <div className="card-value">{fmt(summary?.totalIncome)}</div>
        <div className="card-sub">This month</div>
      </div>

      {/* Total Expenses */}
      <div className="summary-card summary-card-expense">
        <div className="card-icon-row">
          <span className="card-label">Total Expenses</span>
          <span className="card-icon-wrap">↓</span>
        </div>
        <div className="card-value">{fmt(totalExpenses)}</div>
        <div className="card-sub">This month</div>
      </div>

      {/* Net Balance */}
      <div className="summary-card summary-card-balance">
        <div className="card-icon-row">
          <span className="card-label">Net Balance</span>
          <span className="card-icon-wrap">◈</span>
        </div>
        <div className="card-value">{fmt(summary?.savings)}</div>
        <div className="card-sub">
          {(summary?.savings ?? 0) >= 0 ? "↗ Surplus" : "↘ Deficit"}
        </div>
      </div>

      {/* Budget Status */}
      <div className="summary-card summary-card-budget">
        <div className="card-icon-row">
          <span className="card-label card-label-dark">Budget Status</span>
          <span className="card-icon-wrap card-icon-wrap-light">◧</span>
        </div>
        <div
          className="card-value card-value-dark"
          style={{ color: budgetUsed > 90 ? "var(--red)" : budgetUsed > 70 ? "var(--amber)" : "var(--indigo)" }}
        >
          {fmt(remaining < 0 ? 0 : remaining)}
        </div>
        <div className="card-sub-dark">{budgetUsed}% of budget used</div>
        <div className="budget-card-progress-track">
          <div
            className="budget-card-progress-fill"
            style={{
              width: `${Math.min(budgetUsed, 100)}%`,
              background: budgetUsed > 90 ? "var(--red)" : budgetUsed > 70 ? "var(--amber)" : "var(--indigo)",
            }}
          />
        </div>
      </div>
    </div>
  );
}
