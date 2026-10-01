import PasswordInput from "../components/PasswordInput.jsx";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/dataService.js";

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const USERNAME_PATTERN = /^[A-Za-z0-9_.]{3,30}$/;

// Admin creates a customer with a starting password they can share with the customer
export default function AddCustomer() {
  const [form, setForm] = useState({ name: "", email: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!form.name.trim()) return setError("Name is required.");
    if (!EMAIL_PATTERN.test(form.email.trim())) return setError("Enter a valid email address.");
    if (!USERNAME_PATTERN.test(form.username.trim())) {
      return setError("Username must be 3 to 30 characters: letters, numbers, dots, or underscores.");
    }
    if (form.password.length < 8) return setError("Starting password must be at least 8 characters.");

    setLoading(true);
    try {
      const customer = await api.register({
        name: form.name.trim(),
        email: form.email.trim(),
        username: form.username.trim(),
        password: form.password,
      });
      navigate(`/customers/${customer.userId}`, {
        state: { message: `Customer ${customer.name} created!` },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h1>Add Customer</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Name</label>
        <input id="name" value={form.name} onChange={update("name")} />

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={update("email")} />

        <label htmlFor="username">Username</label>
        <input id="username" value={form.username} onChange={update("username")} />

        <label htmlFor="password">Starting Password</label>
        <PasswordInput id="password" value={form.password} onChange={update("password")} />

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save Customer"}
          </button>
          <Link to="/customers" className="btn">Cancel</Link>
        </div>
      </form>
    </div>
  );
}
