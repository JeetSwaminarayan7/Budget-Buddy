import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadPdf, confirmUpload } from "./api";

const fmt = (n) =>
  new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    signDisplay: "always",
  }).format(n);

export default function Upload() {
  const [dragging, setDragging]   = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [preview, setPreview]     = useState(null);
  const [saving, setSaving]       = useState(false);
  const [success, setSuccess]     = useState(null);
  const fileInputRef              = useRef(null);
  const navigate                  = useNavigate();

  function handleDragOver(e) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    setDragging(false);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }

  function handleFileInput(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
  }

  async function processFile(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }
    setError(null);
    setPreview(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await uploadPdf(formData);
      if (result.error) {
        setError(result.error);
      } else {
        setPreview(result.transactions);
      }
    } catch {
      setError("Could not reach the server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  function removeTransaction(index) {
    setPreview((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleConfirm() {
    setSaving(true);
    setError(null);
    try {
      const result = await confirmUpload(preview);
      if (result.error) {
        setError(result.error);
      } else {
        setSuccess(result.message);
        setTimeout(() => navigate("/"), 2000);
      }
    } catch {
      setError("Failed to save transactions. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  function handleReset() {
    setPreview(null);
    setError(null);
    setSuccess(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  if (success) {
    return (
      <main className="main-content">
        <div className="upload-message upload-message-success">
          <span>✓</span>
          {success} — redirecting to dashboard…
        </div>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="main-content">
        <div className="upload-loading">
          <div className="upload-spinner" />
          Extracting transactions with AI…
        </div>
      </main>
    );
  }

  return (
    <main className="main-content">
      {error && (
        <div className="upload-message upload-message-error">
          <span>⚠</span> {error}
        </div>
      )}

      {!preview ? (
        <div
          className={`upload-zone${dragging ? " upload-zone-dragging" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-zone-icon">📄</div>
          <p className="upload-zone-title">Drop your bank statement here</p>
          <p className="upload-zone-sub">
            Supports PDF files from any UK bank · Powered by AI
          </p>
          <button
            className="upload-browse-btn"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
          >
            Browse files
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            onChange={handleFileInput}
          />
        </div>
      ) : (
        <div className="chart-card">
          <div className="chart-card-header">
            <h2 className="chart-title">Extracted Transactions</h2>
            <span className="chart-badge">{preview.length} found</span>
          </div>

          <div className="transactions-list">
            {preview.map((tx, i) => {
              const displayAmount =
                tx.type === "debit"
                  ? -Math.abs(tx.amount)
                  : Math.abs(tx.amount);
              return (
                <div className="tx-row" key={i}>
                  <div className="tx-icon">
                    {tx.type === "credit" ? "💰" : "💳"}
                  </div>
                  <div className="tx-info">
                    <span className="tx-desc">{tx.description}</span>
                    <span className="tx-date">{tx.date}</span>
                  </div>
                  <span
                    className="tx-category"
                    style={{
                      background:
                        tx.type === "credit"
                          ? "var(--green-subtle)"
                          : "var(--surface-2)",
                      color:
                        tx.type === "credit"
                          ? "var(--green)"
                          : "var(--text-muted)",
                    }}
                  >
                    {tx.type === "credit" ? "Credit" : "Debit"}
                  </span>
                  <span
                    className={`tx-amount ${
                      displayAmount > 0 ? "amount-pos" : "amount-neg"
                    }`}
                  >
                    {fmt(displayAmount)}
                  </span>
                  <button
                    className="tx-remove-btn"
                    onClick={() => removeTransaction(i)}
                    title="Remove"
                  >
                    ✕
                  </button>
                </div>
              );
            })}
          </div>

          <div className="upload-actions">
            <button className="upload-discard-btn" onClick={handleReset}>
              Discard
            </button>
            <button
              className="upload-confirm-btn"
              onClick={handleConfirm}
              disabled={saving || preview.length === 0}
            >
              {saving
                ? "Saving…"
                : `Confirm & Save ${preview.length} Transaction${preview.length !== 1 ? "s" : ""}`}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
