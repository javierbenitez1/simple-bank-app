import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, formatDate, formatMoney } from "../api.js";

const LABELS = {
  DEPOSIT: "Deposit",
  WITHDRAW: "Withdrawal",
  TRANSFER_IN: "Transfer In",
  TRANSFER_OUT: "Transfer Out",
};
const MONEY_OUT = ["WITHDRAW", "TRANSFER_OUT"];

export default function Transactions() {
  const { id } = useParams();
  const [transactions, setTransactions] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getTransactions(id).then(setTransactions).catch((err) => setError(err.message));
  }, [id]);

  return (
    <div className="card">
      <h1>Transaction History</h1>
      <p className="muted">Account #{id}</p>

      {error && <p className="error">{error}</p>}
      {!error && !transactions && <p className="muted">Loading transactions...</p>}
      {transactions && transactions.length === 0 && (
        <p className="muted">No transactions yet. Make a deposit to get started.</p>
      )}

      {transactions && transactions.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => {
                const isOut = MONEY_OUT.includes(t.type);
                return (
                  <tr key={t.transactionId}>
                    <td>#{t.transactionId}</td>
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

      <div className="actions">
        <Link to={`/accounts/${id}`} className="btn">Back to Account</Link>
      </div>
    </div>
  );
}
