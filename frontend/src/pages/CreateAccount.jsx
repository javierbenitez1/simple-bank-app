import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export default function CreateAccount() {
  const [form, setForm] = useState({ name: "", email: "", accountType: "SAVINGS" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!form.name.trim()) return setError("Name is required.");
    if (!EMAIL_PATTERN.test(form.email.trim())) return setError("Enter a valid email address.");

    setLoading(true);
    try {
      let user;
      try {
        user = await api.createUser(form.name.trim(), form.email.trim());
      } catch (err) {
        if (err.status !== 409) throw err;
        // Email already exists: this is a returning customer, so open another account for them
        const users = await api.listUsers();
        user = users.find((u) => u.email.toLowerCase() === form.email.trim().toLowerCase());
        if (!user) throw err;
      }
      const account = await api.createAccount(user.userId, form.accountType);
      navigate(`/accounts/${account.accountId}`, {
        state: { message: `Account #${account.accountId} created for ${account.userName}!` },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h1>Create Account</h1>
      <p className="muted">Already a customer? Use the same email to open another account.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Name</label>
        <input id="name" value={form.name} onChange={update("name")} placeholder="Javier Benitez" />

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={update("email")} placeholder="javier@example.com" />

        <label htmlFor="accountType">Account Type</label>
        <select id="accountType" value={form.accountType} onChange={update("accountType")}>
          <option value="SAVINGS">Savings</option>
          <option value="CHECKING">Checking</option>
        </select>

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Creating..." : "Submit"}
          </button>
          <Link to="/" className="btn">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
