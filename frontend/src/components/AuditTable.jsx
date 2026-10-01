import { formatDate, formatMoney } from "../services/dataService.js";

function accountsLabel(log) {
  const from = log.fromAccountId ? `#${log.fromAccountId}` : "";
  const to = log.toAccountId ? `#${log.toAccountId}` : "";
  if (from && to && from !== to) return `${from} → ${to}`;
  return from || to;
}

// Reused by the Admin Dashboard and the Fraud Monitor
export default function AuditTable({ logs, showReason = false }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>When</th>
            <th>Action</th>
            <th>Status</th>
            <th>Amount</th>
            <th>By</th>
            <th>Accounts</th>
            {showReason && <th>Reason</th>}
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.auditId}>
              <td>{formatDate(log.timestamp)}</td>
              <td>{log.action}</td>
              <td>
                <span className={log.status === "SUCCESS" ? "status status-success" : "status status-failed"}>
                  {log.status}
                </span>
              </td>
              <td>{formatMoney(log.amount)}</td>
              <td>{log.performedByName ?? "Unknown"}</td>
              <td>{accountsLabel(log)}</td>
              {showReason && <td className="reason">{log.reason ?? ""}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
