import Spinner from "../components/Spinner.jsx";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api, formatMoney } from "../services/dataService.js";

export default function AccountDetails() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [account, setAccount] = useState(null);
  const [error, setError] = useState("");
  const message = location.state?.message;

  useEffect(() => {
    api.getAccount(id).then(setAccount).catch((err) => setError(err.message));
  }, [id]);

  if (error) {
    return (
      <div className="card">
        <h1>Account Details</h1>
        <p className="error">{error}</p>
        <div className="actions">
          <Link to="/" className="btn">Back to Home</Link>
        </div>
      </div>
    );
  }

  if (!account) {
    return <div className="card"><Spinner message="Loading account..." /></div>;
  }

  return (
    <div className="card">
      {message && <p className="success">{message}</p>}
      <h1>Account Details</h1>

      <dl className="details">
        <div><dt>Account ID</dt><dd>#{account.accountId}</dd></div>
        <div><dt>Account Holder</dt><dd>{account.userName}</dd></div>
        <div><dt>Account Type</dt><dd>{account.accountType}</dd></div>
      </dl>

      <div className="balance">
        <span>Balance</span>
        <strong>{formatMoney(account.balance)}</strong>
      </div>

      <div className="actions">
        <button className="btn btn-primary" onClick={() => navigate(`/accounts/${id}/deposit`)}>Deposit</button>
        <button className="btn btn-primary" onClick={() => navigate(`/accounts/${id}/withdraw`)}>Withdraw</button>
        <button className="btn" onClick={() => navigate(`/accounts/${id}/transactions`)}>View Transactions</button>
        <Link to="/" className="btn">Home</Link>
      </div>
    </div>
  );
}
