import PasswordInput from "../components/PasswordInput.jsx";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!form.username.trim() || !form.password) return setError("Enter your username and password.");

    setLoading(true);
    try {
      const user = await login(form.username.trim(), form.password);
      const home = user.role === "ADMIN" ? "/admin" : "/dashboard";
      navigate(location.state?.from ?? home, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card auth-card">
      <h1>Welcome to Simple Bank</h1>
      <p className="muted">Log in with your username and password.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input id="username" value={form.username} onChange={update("username")} autoComplete="username" autoFocus />

        <label htmlFor="password">Password</label>
        <PasswordInput id="password" value={form.password} onChange={update("password")} autoComplete="current-password" />

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Log In"}
          </button>
        </div>
      </form>

      <p className="auth-switch">
        New here? <Link to="/register">Create an account</Link>
      </p>
    </div>
  );
}
