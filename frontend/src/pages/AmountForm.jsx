import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, formatMoney } from "../services/dataService.js";

export default function AmountForm({ mode }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const isDeposit = mode === "deposit";
  const [account, setAccount] = useState(null);
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getAccount(id).then(setAccount).catch((err) => setError(err.message));
  }, [id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const value = Number(amount);

    // Show validation messages before calling the API
    if (!amount || value <= 0) return setError("Amount must be greater than $0.");
    if (!/^\d+(\.\d{1,2})?$/.test(amount)) return setError("Amount can have at most 2 decimal places.");
    if (!isDeposit && account && value > account.balance) {
      return setError(`Insufficient funds. Your balance is ${formatMoney(account.balance)}.`);
    }

    setLoading(true);
    try {
      const updated = isDeposit ? await api.deposit(id, value) : await api.withdraw(id, value);
      navigate(`/accounts/${id}`, {
        state: {
          message: `${isDeposit ? "Deposited" : "Withdrew"} ${formatMoney(value)}. New balance: ${formatMoney(updated.balance)}`,
        },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h1>{isDeposit ? "Deposit Money" : "Withdraw Money"}</h1>
      {account && (
        <p className="muted">
          Account #{account.accountId} · {account.userName} · Current balance {formatMoney(account.balance)}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <label htmlFor="amount">Amount</label>
        <input
          id="amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="0.00"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          autoFocus
        />

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Processing..." : "Submit"}
          </button>
          <Link to={`/accounts/${id}`} className="btn">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
