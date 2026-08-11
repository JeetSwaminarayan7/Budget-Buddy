import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const fmt = (n) =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" }).format(n);

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <div className="tooltip-title">{label}</div>
        {payload.map((p) => (
          <div key={p.name} style={{ color: p.fill }}>
            {p.name}: <strong>{fmt(p.value)}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function IncomeExpenseChart({ breakdown = [], income = 0 }) {
  const expenseData = breakdown.filter((d) => d.value > 0);

  const data = [
    ...expenseData.map((d) => ({
      name:     d.name.length > 10 ? d.name.slice(0, 9) + "…" : d.name,
      Income:   0,
      Expenses: d.value,
    })),
    { name: "Income", Income: income, Expenses: 0 },
  ];

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} barGap={2} barSize={16}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Sans" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "DM Sans" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `£${v}`}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: "var(--surface-hover)" }} />
        <Legend
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: 12, fontFamily: "DM Sans", paddingTop: 8 }}
        />
        <Bar dataKey="Income"   fill="var(--green)" radius={[4, 4, 0, 0]} />
        <Bar dataKey="Expenses" fill="var(--red)"   radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
