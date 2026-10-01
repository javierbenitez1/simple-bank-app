import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api, formatMoney } from "../services/dataService.js";
import Spinner from "../components/Spinner.jsx";

export default function Transfer() {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState(null);
  const [form, setForm] = useState({ fromAccountId: "", toAccountId: "", amount: "" });
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .getCustomerAccounts(user.userId)
      .then((list) => {
        setAccounts(list);
        if (list.length) setForm((f) => ({ ...f, fromAccountId: String(list[0].accountId) }));
      })
      .catch((err) => setError(err.message));
  }, [user.userId]);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });
  const source = accounts?.find((a) => String(a.accountId) === form.fromAccountId);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    const amount = Number(form.amount);
    const toId = Number(form.toAccountId);

    // Check the obvious mistakes before calling the API
    if (!form.fromAccountId) return setError("Choose an account to send from.");
    if (!toId || toId < 1) return setError("Enter the account ID you're sending to.");
    if (toId === Number(form.fromAccountId)) return setError("You can't transfer to the same account.");
    if (!form.amount || amount <= 0) return setError("Amount must be greater than $0.");
    if (!/^\d+(\.\d{1,2})?$/.test(form.amount)) return setError("Amount can have at most 2 decimal places.");
    if (source && amount > source.balance) {
      return setError(`Insufficient funds. Account #${source.accountId} has ${formatMoney(source.balance)}.`);
    }

    setLoading(true);
    try {
      const res = await api.transfer(Number(form.fromAccountId), toId, amount);
      setResult(res);
      setAccounts((list) =>
        list.map((a) => (a.accountId === res.fromAccount.accountId ? { ...a, balance: res.fromAccount.balance } : a))
      );
      setForm((f) => ({ ...f, toAccountId: "", amount: "" }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!accounts && !error) return <div className="card"><Spinner message="Loading your accounts..." /></div>;

  if (accounts && accounts.length === 0) {
    return (
      <div className="card">
        <h1>Transfer Money</h1>
        <p className="muted">You need an account before you can send money.</p>
        <div className="actions"><Link to="/create" className="btn btn-primary">Open Account</Link></div>
      </div>
    );
  }

  return (
    <div className="card">
      <h1>Transfer Money</h1>
      <p className="muted">Send money from one of your accounts to any account at Simple Bank.</p>

      {result && (
        <p className="success">
          Sent {formatMoney(result.amount)} to account #{result.toAccount.accountId} ({result.toAccount.userName}).
          Account #{result.fromAccount.accountId} now has {formatMoney(result.fromAccount.balance)}.
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <label htmlFor="fromAccountId">From</label>
        <select id="fromAccountId" value={form.fromAccountId} onChange={update("fromAccountId")}>
          {(accounts ?? []).map((a) => (
            <option key={a.accountId} value={a.accountId}>
              #{a.accountId} {a.accountType} · {formatMoney(a.balance)}
            </option>
          ))}
        </select>

        <label htmlFor="toAccountId">To Account ID</label>
        <input id="toAccountId" type="number" min="1" placeholder="e.g. 4" value={form.toAccountId} onChange={update("toAccountId")} />

        <label htmlFor="amount">Amount</label>
        <input id="amount" type="number" min="0" step="0.01" placeholder="0.00" value={form.amount} onChange={update("amount")} />

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send Money"}
          </button>
          <Link to="/dashboard" className="btn">Back to Dashboard</Link>
        </div>
      </form>
    </div>
  );
}
