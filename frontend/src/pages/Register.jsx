import PasswordInput from "../components/PasswordInput.jsx";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const USERNAME_PATTERN = /^[A-Za-z0-9_.]{3,30}$/;

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!form.name.trim()) return setError("Name is required.");
    if (!EMAIL_PATTERN.test(form.email.trim())) return setError("Enter a valid email address.");
    if (!USERNAME_PATTERN.test(form.username.trim())) {
      return setError("Username must be 3 to 30 characters: letters, numbers, dots, or underscores.");
    }
    if (form.password.length < 8) return setError("Password must be at least 8 characters.");

    setLoading(true);
    try {
      await register({
        name: form.name.trim(),
        email: form.email.trim(),
        username: form.username.trim(),
        password: form.password,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message); // e.g. the username "admin" is reserved, or the email is taken
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card auth-card">
      <h1>Create Your Account</h1>
      <p className="muted">Sign up to start banking with Simple Bank.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Full Name</label>
        <input id="name" value={form.name} onChange={update("name")} placeholder="Javier Benitez" />

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={update("email")} placeholder="javier@example.com" />

        <label htmlFor="username">Username</label>
        <input id="username" value={form.username} onChange={update("username")} autoComplete="username" />

        <label htmlFor="password">Password</label>
        <PasswordInput id="password" value={form.password} onChange={update("password")} autoComplete="new-password" />

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Register"}
          </button>
        </div>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
