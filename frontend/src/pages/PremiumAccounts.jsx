import { useEffect, useState } from "react";
import { api, formatMoney } from "../services/dataService.js";
import AccountList from "../components/AccountList.jsx";
import Spinner from "../components/Spinner.jsx";

export default function PremiumAccounts() {
  const [threshold, setThreshold] = useState("1000");
  const [accounts, setAccounts] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load(value) {
    setError("");
    if (value === "" || Number(value) < 0) {
      setError("Enter a threshold of $0 or more.");
      return;
    }
    setLoading(true);
    try {
      setAccounts(await api.getPremiumAccounts(value));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load("1000");
  }, []);

  return (
    <div className="card">
      <h1>Premium Accounts</h1>
      <p className="muted">Every account with a balance at or above the threshold.</p>

      <form
        className="row filter-row"
        onSubmit={(e) => {
          e.preventDefault();
          load(threshold);
        }}
      >
        <input
          type="number"
          min="0"
          step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          aria-label="Minimum balance"
        />
        <button className="btn btn-primary" type="submit">Filter</button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <Spinner message="Finding premium accounts..." />}
      {!loading && accounts && (
        <AccountList
          accounts={accounts}
          showHolder
          emptyMessage={`No accounts with ${formatMoney(threshold || 0)} or more.`}
        />
      )}
    </div>
  );
}
