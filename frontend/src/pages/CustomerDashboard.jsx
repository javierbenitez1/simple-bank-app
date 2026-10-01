import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api, formatDate, formatMoney } from "../services/dataService.js";
import AccountList from "../components/AccountList.jsx";
import BarChart from "../components/BarChart.jsx";
import Spinner from "../components/Spinner.jsx";

const LABELS = {
  DEPOSIT: "Deposit",
  WITHDRAW: "Withdrawal",
  TRANSFER_IN: "Transfer In",
  TRANSFER_OUT: "Transfer Out",
};
const MONEY_IN = ["DEPOSIT", "TRANSFER_IN"];
const MONEY_OUT = ["WITHDRAW", "TRANSFER_OUT"];
const sum = (list) => list.reduce((total, t) => total + t.amount, 0);

export default function CustomerDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [allTransactions, setAllTransactions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const dashboard = await api.getCustomerDashboard(user.userId);
        // Load every account's history at the same time for the charts
        const histories = await Promise.all(dashboard.accounts.map((a) => api.getTransactions(a.accountId)));
        if (!cancelled) {
          setData(dashboard);
          setAllTransactions(histories.flat());
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [user.userId]);

  if (error) return <div className="card"><h1>My Dashboard</h1><p className="error">{error}</p></div>;
  if (!data) return <div className="card"><Spinner message="Loading your dashboard..." /></div>;

  const { customer, accounts, totalBalance, recentTransactions } = data;

  const moneyFlow = [
    { label: "Money In", value: sum(allTransactions.filter((t) => MONEY_IN.includes(t.type))), color: "var(--success)" },
    { label: "Money Out", value: sum(allTransactions.filter((t) => MONEY_OUT.includes(t.type))), color: "var(--error)" },
  ];
  const balances = accounts.map((a) => ({
    label: `#${a.accountId} ${a.accountType === "SAVINGS" ? "Savings" : "Checking"}`,
    value: a.balance,
  }));

  return (
    <div className="card">
      <div className="card-header">
        <h1>Hi, {customer.name.split(" ")[0]}</h1>
        <div className="row">
          <Link to="/transfer" className="btn">Transfer</Link>
          <Link to="/create" className="btn btn-primary">Open Account</Link>
        </div>
      </div>
      <p className="muted">
        {customer.username ? `@${customer.username} · ` : ""}{customer.email}
      </p>

      <div className="balance">
        <span>Total across {accounts.length} account{accounts.length === 1 ? "" : "s"}</span>
        <strong>{formatMoney(totalBalance)}</strong>
      </div>

      {accounts.length > 0 && (
        <div className="chart-grid">
          <BarChart title="Money In vs Out" data={moneyFlow} />
          <BarChart title="Balance by Account" data={balances} />
        </div>
      )}

      <h2>My Accounts</h2>
      <AccountList accounts={accounts} emptyMessage="You don't have any accounts yet. Click Open Account to get started." />

      <h2>Recent Transactions</h2>
      {recentTransactions.length === 0 ? (
        <p className="muted">No transactions yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Account</th><th>Type</th><th>Amount</th><th>Date</th></tr>
            </thead>
            <tbody>
              {recentTransactions.map((t) => {
                const isOut = MONEY_OUT.includes(t.type);
                return (
                  <tr key={t.transactionId}>
                    <td>#{t.accountId}</td>
                    <td>{LABELS[t.type] ?? t.type}</td>
                    <td className={isOut ? "amount-out" : "amount-in"}>
                      {isOut ? "-" : "+"}{formatMoney(t.amount)}
                    </td>
                    <td>{formatDate(t.date)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
