import { Link } from "react-router-dom";
import { formatMoney } from "../services/dataService.js";

// Reused by Customer Details and Premium Accounts, with different props
export default function AccountList({ accounts, showHolder = false, emptyMessage = "No accounts yet." }) {
  if (accounts.length === 0) return <p className="muted">{emptyMessage}</p>;

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Account ID</th>
            {showHolder && <th>Holder</th>}
            <th>Type</th>
            <th>Balance</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((a) => (
            <tr key={a.accountId}>
              <td>#{a.accountId}</td>
              {showHolder && <td>{a.userName}</td>}
              <td>{a.accountType}</td>
              <td>{formatMoney(a.balance)}</td>
              <td>
                <Link to={`/accounts/${a.accountId}`} className="btn btn-small">Open</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
