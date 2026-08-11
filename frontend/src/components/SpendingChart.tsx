import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import type { TooltipProps } from "recharts";
import type { BreakdownItem } from "../types";

const fmt = (n: number) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" }).format(n);

function CustomTooltip({ active, payload }: TooltipProps<number, string>) {
  if (active && payload && payload.length) {
    const d = payload[0].payload as BreakdownItem;
    return (
      <div className="chart-tooltip">
        <span>{d.icon} {d.name}</span>
        <strong>{fmt(d.value)}</strong>
      </div>
    );
  }
  return null;
}

interface SpendingChartProps {
  data?: BreakdownItem[];
}

export default function SpendingChart({ data = [] }: SpendingChartProps) {
  const active = data.filter((d) => d.value > 0);
  const total  = active.reduce((s, d) => s + d.value, 0);

  if (active.length === 0) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200, color: "var(--text-muted)", fontSize: 13 }}>
        No expenses yet this month
      </div>
    );
  }

  return (
    <>
      <div className="donut-wrapper">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={active}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {active.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="donut-centre">
          <span className="donut-total">{fmt(total)}</span>
          <span className="donut-label">spent</span>
        </div>
      </div>

      <div className="category-legend">
        {active.map((d) => {
          const pct = total > 0 ? Math.round((d.value / total) * 100) : 0;
          return (
            <div className="legend-item" key={d.name}>
              <span className="legend-dot" style={{ background: d.color }} />
              <span className="legend-name">{d.icon} {d.name} {pct}%</span>
              <span className="legend-value">{fmt(d.value)}</span>
            </div>
          );
        })}
      </div>
    </>
  );
}
