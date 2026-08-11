import { useState, useEffect, useMemo } from "react";
import { fetchAllTransactions, fetchCategories, fetchMonths, updateTransaction } from "./api";
import type { Transaction, Category } from "./types";

const fmt = (n: number) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", signDisplay: "always" }).format(n);

const PER_PAGE = 20;

export default function Transactions() {
  const [allTxs, setAllTxs]         = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [months, setMonths]         = useState<string[]>([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState<string | null>(null);

  const [monthFilter, setMonthFilter] = useState("");
  const [catFilter, setCatFilter]     = useState("");
  const [search, setSearch]           = useState("");
  const [page, setPage]               = useState(1);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchAllTransactions(), fetchCategories(), fetchMonths()])
      .then(([txs, cats, ms]) => {
        setAllTxs(txs);
        setCategories(cats);
        setMonths(ms);
      })
      .catch(() => setError("Failed to load transactions. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    return allTxs.filter((tx) => {
      if (monthFilter && !tx.date.startsWith(monthFilter)) return false;
      if (catFilter && tx.category !== catFilter) return false;
      if (search && !tx.description.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [allTxs, monthFilter, catFilter, search]);

  useEffect(() => { setPage(1); }, [monthFilter, catFilter, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const slice      = filtered.slice((page - 1) * PER_PAGE, page * PER_PAGE);

  async function handleCategoryChange(txId: number, newCat: string) {
    const prev = allTxs.find((tx) => tx.id === txId)?.category ?? null;
    setAllTxs((p) =>
      p.map((tx) => (tx.id === txId ? { ...tx, category: newCat } : tx))
    );
    try {
      const res = await updateTransaction(txId, { category: newCat });
      if ("error" in res) throw new Error(res.error);
    } catch (err) {
      // Revert on failure
      setAllTxs((p) =>
        p.map((tx) => (tx.id === txId ? { ...tx, category: prev } : tx))
      );
      const message = err instanceof Error ? err.message : "unknown error";
      setError("Failed to update category: " + message);
    }
  }

  function handleExportCSV() {
    const headers = ["Date", "Description", "Category", "Type", "Amount"];
    const rows = filtered.map((tx) => {
      const amt = tx.type === "debit" ? -Math.abs(tx.amount) : Math.abs(tx.amount);
      return [
        tx.date,
        `"${(tx.description || "").replace(/"/g, '""')}"`,
        tx.category || "",
        tx.type,
        amt.toFixed(2),
      ];
    });
    const csv  = [headers, ...rows].map((r) => r.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `transactions${monthFilter ? `-${monthFilter}` : ""}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (loading) return (
    <main className="main-content">
      <div className="loading-state">Loading transactions…</div>
    </main>
  );

  if (error) return (
    <main className="main-content">
      <div className="upload-message upload-message-error"><span>⚠</span> {error}</div>
    </main>
  );

  return (
    <main className="main-content">
      <div className="page-header">
        <h1 className="page-title">Transactions</h1>
        <p className="page-subtitle">Showing {filtered.length} transaction{filtered.length !== 1 ? "s" : ""}</p>
      </div>

      {/* Filters */}
      <div className="tx-filters">
        <div className="tx-search-wrap">
          <span className="tx-search-icon">⌕</span>
          <input
            className="tx-search"
            type="text"
            placeholder="Search transactions…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          className="tx-filter-select"
          value={monthFilter}
          onChange={(e) => setMonthFilter(e.target.value)}
        >
          <option value="">All months</option>
          {months.map((m) => (
            <option key={m} value={m}>
              {new Date(m + "-01").toLocaleString("en-GB", { month: "long", year: "numeric" })}
            </option>
          ))}
        </select>

        <select
          className="tx-filter-select"
          value={catFilter}
          onChange={(e) => setCatFilter(e.target.value)}
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.name} value={c.name}>{c.icon} {c.name}</option>
          ))}
        </select>

        <button
          className="csv-export-btn"
          onClick={handleExportCSV}
          disabled={filtered.length === 0}
          title="Download current view as CSV"
        >
          ↓ Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="chart-card">
        <div className="tx-table-head">
          <span />
          <span className="tx-head-label">Date</span>
          <span className="tx-head-label">Description</span>
          <span className="tx-head-label">Category</span>
          <span className="tx-head-label">Type</span>
          <span className="tx-head-label tx-head-right">Amount</span>
        </div>

        <div className="transactions-list">
          {slice.length === 0 ? (
            <div className="tx-empty">No transactions match your filters.</div>
          ) : (
            slice.map((tx) => {
              const displayAmount = tx.type === "debit" ? -Math.abs(tx.amount) : Math.abs(tx.amount);
              return (
                <div className="tx-row tx-row-full" key={tx.id}>
                  <div className="tx-icon">{tx.icon || "💳"}</div>
                  <span className="tx-full-date">{tx.date}</span>
                  <span className="tx-desc">{tx.description}</span>

                  <div>
                    <select
                      className="tx-cat-select"
                      value={tx.category || ""}
                      onChange={(e) => handleCategoryChange(tx.id, e.target.value)}
                    >
                      {categories.map((c) => (
                        <option key={c.name} value={c.name}>{c.icon} {c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <span
                      className="tx-category"
                      style={{
                        background: tx.type === "credit" ? "var(--green-subtle)" : "var(--surface-2)",
                        color:      tx.type === "credit" ? "var(--green)"        : "var(--text-muted)",
                      }}
                    >
                      {tx.type === "credit" ? "Credit" : "Debit"}
                    </span>
                  </div>

                  <span className={`tx-amount ${displayAmount > 0 ? "amount-pos" : "amount-neg"}`}>
                    {fmt(displayAmount)}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {totalPages > 1 && (
          <div className="tx-pagination">
            <button
              className="tx-page-btn"
              onClick={() => setPage((p) => p - 1)}
              disabled={page === 1}
            >
              ← Prev
            </button>
            <span className="tx-page-info">Page {page} of {totalPages}</span>
            <button
              className="tx-page-btn"
              onClick={() => setPage((p) => p + 1)}
              disabled={page === totalPages}
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
