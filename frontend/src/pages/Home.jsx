import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [accountId, setAccountId] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function handleView(e) {
    e.preventDefault();
    if (!accountId || Number(accountId) < 1) {
      setError("Enter a valid account ID.");
      return;
    }
    navigate(`/accounts/${accountId}`);
  }

  return (
    <div className="card">
      <h1>Welcome to Simple Bank</h1>
      <p className="muted">Open a new account or look up an existing one.</p>

      <div className="home-actions">
        <button className="btn btn-primary" onClick={() => navigate("/create")}>
          Create Account
        </button>
      </div>

      <form onSubmit={handleView} className="view-form">
        <label htmlFor="accountId">View Account</label>
        <div className="row">
          <input
            id="accountId"
            type="number"
            min="1"
            placeholder="Account ID"
            value={accountId}
            onChange={(e) => {
              setAccountId(e.target.value);
              setError("");
            }}
          />
          <button className="btn" type="submit">View</button>
        </div>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
