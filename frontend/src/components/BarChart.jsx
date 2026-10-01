import { formatMoney } from "../services/dataService.js";

// A simple bar chart built with plain divs, so there's no chart library to install
export default function BarChart({ title, data, format = formatMoney }) {
  const max = Math.max(...data.map((d) => d.value), 0);

  return (
    <div className="chart">
      {title && <h3 className="chart-title">{title}</h3>}
      {data.length === 0 && <p className="muted">Nothing to show yet.</p>}
      {data.map((d) => (
        <div className="chart-row" key={d.label}>
          <span className="chart-label">{d.label}</span>
          <div className="chart-track">
            <div
              className="chart-bar"
              style={{
                width: max ? `${(d.value / max) * 100}%` : "0%",
                background: d.color ?? "var(--primary)",
              }}
            />
          </div>
          <span className="chart-value">{format(d.value)}</span>
        </div>
      ))}
    </div>
  );
}
