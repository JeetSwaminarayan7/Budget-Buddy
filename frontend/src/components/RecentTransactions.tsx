import { useNavigate } from "react-router-dom";
import type { Transaction } from "../types";

const fmt = (n: number) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", signDisplay: "always" }).format(n);

interface RecentTransactionsProps {
  transactions?: Transaction[];
}

export default function RecentTransactions({ transactions = [] }: RecentTransactionsProps) {
  const navigate = useNavigate();

  if (transactions.length === 0) {
    return (
      <div className="tx-empty">
        No transactions yet.{" "}
        <button
          onClick={() => navigate("/upload")}
          style={{ background: "none", border: "none", color: "var(--indigo)", cursor: "pointer", fontSize: 13.5, fontWeight: 500 }}
        >
          Upload a bank statement →
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="transactions-list">
        {transactions.map((tx) => {
          const displayAmount = tx.type === "debit" ? -Math.abs(tx.amount) : Math.abs(tx.amount);
          const catBg  = tx.type === "credit" ? "var(--green-subtle)"  : "var(--surface-2)";
          const catClr = tx.type === "credit" ? "var(--green)"         : "var(--text-muted)";

          return (
            <div className="tx-row" key={tx.id}>
              <div className="tx-icon">{tx.icon || "💳"}</div>
              <div className="tx-info">
                <span className="tx-desc">{tx.description}</span>
                <span className="tx-date">{tx.date}</span>
              </div>
              <span className="tx-category" style={{ background: catBg, color: catClr }}>
                {tx.category || "Uncategorised"}
              </span>
              <span className={`tx-amount ${displayAmount > 0 ? "amount-pos" : "amount-neg"}`}>
                {fmt(displayAmount)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 16, textAlign: "right" }}>
        <button className="see-all-btn" onClick={() => navigate("/transactions")}>
          See all transactions →
        </button>
      </div>
    </>
  );
}
