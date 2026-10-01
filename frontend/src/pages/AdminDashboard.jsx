import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatMoney } from "../services/dataService.js";
import AuditTable from "../components/AuditTable.jsx";
import BarChart from "../components/BarChart.jsx";
import Spinner from "../components/Spinner.jsx";
import StatCard from "../components/StatCard.jsx";

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  // The SERVER decides who gets in. A customer token gets a 403 back, and we show it.
  useEffect(() => {
    Promise.all([api.getAdminDashboard(), api.getAuditLogs()])
      .then(([dashboard, auditLogs]) => {
        setData(dashboard);
        setLogs(auditLogs);
      })
      .catch((err) => setError(err.status === 403 ? `403 Forbidden: ${err.message}` : err.message));
  }, []);

  if (error) {
    return (
      <div className="card">
        <h1>Admin Dashboard</h1>
        <p className="error">{error}</p>
        <div className="actions"><Link to="/" className="btn">Back to my dashboard</Link></div>
      </div>
    );
  }

  if (!data) return <div className="card"><Spinner message="Loading admin dashboard..." /></div>;

  const successful = logs.filter((log) => log.status === "SUCCESS");
  const totalFor = (action) =>
    successful.filter((log) => log.action === action).reduce((total, log) => total + log.amount, 0);

  const moneyByType = [
    { label: "Deposits", value: totalFor("DEPOSIT"), color: "var(--success)" },
    { label: "Withdrawals", value: totalFor("WITHDRAW"), color: "var(--error)" },
    { label: "Transfers", value: totalFor("TRANSFER"), color: "var(--primary)" },
  ];
  const outcomes = [
    { label: "Successful", value: successful.length, color: "var(--success)" },
    { label: "Failed", value: logs.length - successful.length, color: "var(--error)" },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h1>Admin Dashboard</h1>
        <Link to="/fraud" className="btn">Open Fraud Monitor</Link>
      </div>
      <p className="muted">Signed in as {data.adminName}</p>

      <div className="stats">
        <StatCard label="Customers" value={data.totalCustomers} />
        <StatCard label="Accounts" value={data.totalAccounts} />
        <StatCard label="Total Deposits" value={formatMoney(data.totalDeposits)} />
        <StatCard label="Failed Attempts" value={data.failedAttempts} />
      </div>

      <div className="chart-grid">
        <BarChart title="Money Moved by Type" data={moneyByType} />
        <BarChart title="Successful vs Failed" data={outcomes} format={(n) => n} />
      </div>

      <h2>Recent Activity</h2>
      {data.recentActivity.length === 0 ? (
        <p className="muted">No activity yet.</p>
      ) : (
        <AuditTable logs={data.recentActivity} />
      )}
    </div>
  );
}
