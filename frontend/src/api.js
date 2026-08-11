// In local dev (via the nginx/Vite proxy) the frontend and backend share an
// origin, so a relative "/api" works. In production the frontend (Vercel)
// and backend (Render) are on different domains, so VITE_API_URL must be
// set to the full backend URL, e.g. https://budget-buddy-api.onrender.com/api
const BASE = import.meta.env.VITE_API_URL || "/api";

async function req(path, opts = {}) {
  const isForm = opts.body instanceof FormData;
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: isForm ? {} : { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const fetchMe  = ()     => req("/auth/me");
export const login    = (data) => req("/auth/login",    { method: "POST", body: JSON.stringify(data) });
export const register = (data) => req("/auth/register", { method: "POST", body: JSON.stringify(data) });
export const logout   = ()     => req("/auth/logout",   { method: "POST" });

// ── Data ──────────────────────────────────────────────────────────────────────

export const fetchSummary   = (month)      => req(`/summary?month=${month}`);
export const fetchBreakdown = (month)      => req(`/breakdown?month=${month}`);
export const fetchTrend     = ()           => req("/trend");
export const fetchMonths    = ()           => req("/months");
export const fetchCategories = ()          => req("/categories");
export const fetchBudgets   = (month)      => req(`/budgets?month=${month}`);

export const fetchTransactions = (params = {}) =>
  req(`/transactions?${new URLSearchParams(params)}`);

export const fetchAllTransactions = ({ month = "", category = "", search = "", limit = 500 } = {}) => {
  const p = new URLSearchParams({ limit: String(limit) });
  if (month)    p.set("month",    month);
  if (category) p.set("category", category);
  if (search)   p.set("search",   search);
  return req(`/transactions?${p}`);
};

// ── Mutations ─────────────────────────────────────────────────────────────────

export const addTransaction    = (data)       => req("/transactions",       { method: "POST",   body: JSON.stringify(data) });
export const deleteTransaction = (id)         => req(`/transactions/${id}`, { method: "DELETE" });
export const updateTransaction = (id, data)   => req(`/transactions/${id}`, { method: "PATCH",  body: JSON.stringify(data) });

export const updateBudget         = (data)  => req("/budgets",         { method: "PUT", body: JSON.stringify(data) });
export const fetchMonthlyBudget   = ()      => req(`/budget/monthly`);
export const updateMonthlyBudget  = (data)  => req("/budget/monthly",  { method: "PUT", body: JSON.stringify(data) });

export const fetchSettings  = ()     => req("/settings");
export const updateSettings = (data) => req("/settings", { method: "PUT", body: JSON.stringify(data) });

export const createCategory = (data)          => req("/categories",         { method: "POST",   body: JSON.stringify(data) });
export const deleteCategory = (id)            => req(`/categories/${id}`,   { method: "DELETE" });

export const uploadPdf      = (formData)      => req("/upload",             { method: "POST",   body: formData });
export const confirmUpload  = (transactions)  => req("/upload/confirm",     { method: "POST",   body: JSON.stringify({ transactions }) });
