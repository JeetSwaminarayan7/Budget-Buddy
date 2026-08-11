import type {
  Transaction,
  Category,
  Budget,
  BreakdownItem,
  TrendPoint,
  Summary,
  Settings,
  ApiError,
  ExtractedTransaction,
} from "./types";

// In local dev (via the nginx/Vite proxy) the frontend and backend share an
// origin, so a relative "/api" works. In production the frontend (Vercel)
// and backend (Render) are on different domains, so VITE_API_URL must be
// set to the full backend URL, e.g. https://budget-buddy-api.onrender.com/api
const BASE = import.meta.env.VITE_API_URL || "/api";

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: BodyInit | object;
}

async function req<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const isForm = opts.body instanceof FormData;
  const body =
    !isForm && opts.body !== undefined && typeof opts.body !== "string"
      ? JSON.stringify(opts.body)
      : (opts.body as BodyInit | undefined);

  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: isForm ? {} : { "Content-Type": "application/json", ...opts.headers },
    ...opts,
    body,
  });
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: number;
  username: string;
  email: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const fetchMe  = ()                       => req<AuthUser | ApiError>("/auth/me");
export const login    = (data: LoginPayload)      => req<AuthUser | ApiError>("/auth/login",    { method: "POST", body: data });
export const register = (data: RegisterPayload)   => req<AuthUser | ApiError>("/auth/register", { method: "POST", body: data });
export const logout   = ()                        => req<{ message: string }>("/auth/logout", { method: "POST" });

// ── Data ──────────────────────────────────────────────────────────────────────

export const fetchSummary    = (month: string)     => req<Summary>(`/summary?month=${month}`);
export const fetchBreakdown  = (month: string)     => req<BreakdownItem[]>(`/breakdown?month=${month}`);
export const fetchTrend      = ()                  => req<TrendPoint[]>("/trend");
export const fetchMonths     = ()                  => req<string[]>("/months");
export const fetchCategories = ()                  => req<Category[]>("/categories");
export const fetchBudgets    = (month: string)     => req<Budget[]>(`/budgets?month=${month}`);

export interface TransactionQuery {
  month?: string;
  category?: string;
  search?: string;
  limit?: number | string;
}

export const fetchTransactions = (params: Record<string, string> = {}) =>
  req<Transaction[]>(`/transactions?${new URLSearchParams(params)}`);

export const fetchAllTransactions = ({
  month = "",
  category = "",
  search = "",
  limit = 500,
}: TransactionQuery = {}) => {
  const p = new URLSearchParams({ limit: String(limit) });
  if (month) p.set("month", month);
  if (category) p.set("category", category);
  if (search) p.set("search", search);
  return req<Transaction[]>(`/transactions?${p}`);
};

// ── Mutations ─────────────────────────────────────────────────────────────────

export interface NewTransaction {
  date: string;
  description: string;
  amount: number;
  type: "debit" | "credit";
  category: string;
}

export const addTransaction = (data: NewTransaction) =>
  req<{ id: number; message: string }>("/transactions", { method: "POST", body: data });

export const deleteTransaction = (id: number) =>
  req<{ message: string }>(`/transactions/${id}`, { method: "DELETE" });

export const updateTransaction = (id: number, data: Partial<NewTransaction>) =>
  req<{ message: string } | ApiError>(`/transactions/${id}`, { method: "PATCH", body: data });

export interface UpdateBudgetPayload {
  category: string;
  amount: number;
  month: string;
}

export const updateBudget        = (data: UpdateBudgetPayload) =>
  req<{ message: string }>("/budgets", { method: "PUT", body: data });

export const fetchMonthlyBudget  = () => req<{ amount: number }>("/budget/monthly");

export const updateMonthlyBudget = (data: { amount: number }) =>
  req<{ message: string }>("/budget/monthly", { method: "PUT", body: data });

export const fetchSettings  = () => req<Settings>("/settings");

export const updateSettings = (data: Partial<Settings>) =>
  req<{ message: string }>("/settings", { method: "PUT", body: data });

export const createCategory = (data: { name: string; icon?: string; color?: string }) =>
  req<{ id: number; name: string; icon: string; color: string } | ApiError>("/categories", { method: "POST", body: data });

export const deleteCategory = (id: number) =>
  req<{ message: string }>(`/categories/${id}`, { method: "DELETE" });

export const uploadPdf = (formData: FormData) =>
  req<{ transactions: ExtractedTransaction[] } | ApiError>("/upload", { method: "POST", body: formData });

export const confirmUpload = (transactions: ExtractedTransaction[]) =>
  req<{ message: string } | ApiError>("/upload/confirm", { method: "POST", body: { transactions } });
