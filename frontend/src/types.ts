// Shared types matching the Flask backend's actual JSON response shapes
// (see backend/app.py — these are the joined/aliased API shapes the
// frontend receives, not raw DB rows).

export interface User {
  id: number;
  username: string;
  email: string;
  monthly_budget: number;
  savings_goal: number;
}

export interface Category {
  id: number;
  user_id: number;
  name: string;
  icon: string;
  color: string;
}

export type TransactionType = "debit" | "credit";

// Shape of a transaction freshly extracted from a PDF, before it has a
// category assigned (returned by POST /api/upload)
export interface ExtractedTransaction {
  date: string;
  description: string;
  amount: number;
  type: TransactionType;
}
export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  type: TransactionType;
  source: string;
  category: string | null;
  icon: string | null;
  color: string | null;
}

// Shape returned by GET /api/budgets (one row per category)
export interface Budget {
  id: number;
  name: string;
  icon: string;
  color: string;
  budget: number;
  spent: number;
}

// Shape returned by GET /api/breakdown
export interface BreakdownItem {
  name: string;
  icon: string;
  color: string;
  value: number;
}

// Shape returned by GET /api/trend
export interface TrendPoint {
  month: string;
  income: number;
  expenses: number;
}

// Shape returned by GET /api/summary
export interface Summary {
  totalIncome: number;
  totalExpenses: number;
  savings: number;
  savingsRate: number;
  budgetUsed: number;
  totalBudget: number;
}

export interface Settings {
  monthly_budget: number;
  savings_goal: number;
}

export interface ApiError {
  error: string;
}

export interface ApiMessage {
  message: string;
}
