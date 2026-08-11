import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import type { TooltipProps } from "recharts";
import type { TrendPoint } from "../types";

const fmt = (n: number) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" }).format(n);

function CustomTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <div className="tooltip-title">{label}</div>
        {payload.map((p) => (
          <div key={p.name} style={{ color: p.color }}>
            {p.name}: <strong>{fmt(p.value as number)}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

interface TrendChartProps {
  data?: TrendPoint[];
}

export default function TrendChart({ data = [] }: TrendChartProps) {
  if (data.length === 0) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200, color: "var(--text-muted)", fontSize: 13 }}>
        No trend data yet — upload a bank statement to get started
      </div>
    );
  }

  if (data.length === 1) {
    const d = data[0];
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 200, gap: 12 }}>
        <p style={{ color: "var(--text-muted)", fontSize: 13, margin: 0 }}>
          Only one month of data ({d.month}) — upload more statements to see trends
        </p>
        <div style={{ display: "flex", gap: 24 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Income</div>
            <div style={{ fontSize: 20, fontWeight: 600, color: "var(--green)" }}>{fmt(d.income)}</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Expenses</div>
            <div style={{ fontSize: 20, fontWeight: 600, color: "var(--red)" }}>{fmt(d.expenses)}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fill: "var(--text-muted)", fontSize: 12, fontFamily: "DM Sans" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "var(--text-muted)", fontSize: 12, fontFamily: "DM Sans" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `£${v}`}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ stroke: "var(--border)", strokeWidth: 1 }} />
        <Line
          type="monotone"
          dataKey="income"
          name="Income"
          stroke="var(--green)"
          strokeWidth={2.5}
          dot={{ fill: "var(--green)", r: 4, strokeWidth: 0 }}
          activeDot={{ r: 5 }}
        />
        <Line
          type="monotone"
          dataKey="expenses"
          name="Expenses"
          stroke="var(--red)"
          strokeWidth={2.5}
          strokeDasharray="5 4"
          dot={{ fill: "var(--red)", r: 4, strokeWidth: 0 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
