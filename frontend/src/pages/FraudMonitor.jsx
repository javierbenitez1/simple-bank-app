import { useEffect, useState } from "react";
import { api } from "../services/dataService.js";
import AuditFilters from "../components/AuditFilters.jsx";
import AuditTable from "../components/AuditTable.jsx";
import Spinner from "../components/Spinner.jsx";

const DEFAULT_FILTERS = { status: "FAILED", action: "", accountId: "" };

export default function FraudMonitor() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [logs, setLogs] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load(f) {
    setLoading(true);
    setError("");
    try {
      setLogs(await api.getAuditLogs(f));
    } catch (err) {
      setError(err.status === 403 ? `403 Forbidden: ${err.message}` : err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(DEFAULT_FILTERS);
  }, []);

  // Flag any account with 2 or more failed attempts in these results
  const failedByAccount = {};
  (logs ?? [])
    .filter((log) => log.status === "FAILED")
    .forEach((log) => {
      const id = log.fromAccountId ?? log.toAccountId;
      if (id) failedByAccount[id] = (failedByAccount[id] ?? 0) + 1;
    });
  const flagged = Object.entries(failedByAccount)
    .filter(([, count]) => count >= 2)
    .sort((a, b) => b[1] - a[1]);

  return (
    <div className="card">
      <h1>Fraud Monitor</h1>
      <p className="muted">
        Every deposit, withdrawal, and transfer is logged, including failed attempts. Repeated failures can be a sign of fraud.
      </p>

      <AuditFilters
        filters={filters}
        onChange={setFilters}
        onApply={() => load(filters)}
        onReset={() => {
          setFilters(DEFAULT_FILTERS);
          load(DEFAULT_FILTERS);
        }}
      />

      {flagged.length > 0 && (
        <div className="alert-flag">
          <strong>⚠ Flagged accounts:</strong>{" "}
          {flagged.map(([id, count]) => `#${id} (${count} failed)`).join(", ")}
        </div>
      )}

      {error && <p className="error">{error}</p>}
      {loading && <Spinner message="Searching the audit log..." />}
      {!loading && logs && logs.length === 0 && <p className="muted">No activity matches these filters.</p>}
      {!loading && logs && logs.length > 0 && <AuditTable logs={logs} showReason />}
    </div>
  );
}
