import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/dataService.js";

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export default function AddCustomer() {
  const [form, setForm] = useState({ name: "", email: "" });
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
      const customer = await api.createCustomer(form.name.trim(), form.email.trim());
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
        <input id="name" value={form.name} onChange={update("name")} placeholder="Javier Benitez" />

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={update("email")} placeholder="javier@example.com" />

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
