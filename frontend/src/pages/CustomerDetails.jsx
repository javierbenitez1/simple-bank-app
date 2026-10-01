import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api, formatMoney } from "../services/dataService.js";
import AccountList from "../components/AccountList.jsx";
import Spinner from "../components/Spinner.jsx";

export default function CustomerDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const message = useLocation().state?.message;
  const [customer, setCustomer] = useState(null);
  const [accounts, setAccounts] = useState(null);
  const [error, setError] = useState("");

  // One customer has many accounts: load both at the same time
  useEffect(() => {
    Promise.all([api.getCustomer(id), api.getCustomerAccounts(id)])
      .then(([c, a]) => {
        setCustomer(c);
        setAccounts(a);
      })
      .catch((err) => setError(err.message));
  }, [id]);

  async function handleDelete() {
    if (!window.confirm(`Delete ${customer.name}? This can't be undone.`)) return;
    setError("");
    try {
      await api.deleteCustomer(id);
      navigate("/customers");
    } catch (err) {
      setError(err.message);
    }
  }

  if (error && !customer) {
    return (
      <div className="card">
        <h1>Customer</h1>
        <p className="error">{error}</p>
        <div className="actions"><Link to="/customers" className="btn">Back to Customers</Link></div>
      </div>
    );
  }

  if (!customer) {
    return <div className="card"><Spinner message="Loading customer..." /></div>;
  }

  const total = accounts.reduce((sum, a) => sum + a.balance, 0);

  return (
    <div className="card">
      {message && <p className="success">{message}</p>}
      <h1>{customer.name}</h1>
      <p className="muted">Customer #{customer.userId} · {customer.email}</p>
      {error && <p className="error">{error}</p>}

      <div className="balance">
        <span>Total across {accounts.length} account{accounts.length === 1 ? "" : "s"}</span>
        <strong>{formatMoney(total)}</strong>
      </div>

      <h2>Accounts</h2>
      <AccountList accounts={accounts} emptyMessage="This customer doesn't have any accounts yet." />

      <div className="actions">
        <button className="btn btn-danger" onClick={handleDelete}>Delete Customer</button>
        <Link to="/customers" className="btn">Back to Customers</Link>
      </div>
    </div>
  );
}
