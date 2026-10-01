import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../services/dataService.js";

// You're logged in, so we already know who the account is for
export default function CreateAccount() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [accountType, setAccountType] = useState("SAVINGS");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const account = await api.createAccount(user.userId, accountType);
      navigate(`/accounts/${account.accountId}`, {
        state: { message: `Account #${account.accountId} opened!` },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h1>Open Account</h1>
      <p className="muted">Opening a new account for {user.name}.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="accountType">Account Type</label>
        <select id="accountType" value={accountType} onChange={(e) => setAccountType(e.target.value)}>
          <option value="SAVINGS">Savings</option>
          <option value="CHECKING">Checking</option>
        </select>

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Opening..." : "Open Account"}
          </button>
          <Link to="/" className="btn">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
