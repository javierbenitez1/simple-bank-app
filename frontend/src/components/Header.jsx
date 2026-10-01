import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ThemeToggle from "./ThemeToggle.jsx";

const GUEST_LINKS = [
  { to: "/login", label: "Log In" },
  { to: "/register", label: "Register" },
];
const CUSTOMER_LINKS = [
  { to: "/dashboard", label: "My Dashboard" },
  { to: "/transfer", label: "Transfer" },
  { to: "/create", label: "Open Account" },
];
const ADMIN_LINKS = [
  { to: "/admin", label: "Admin" },
  { to: "/fraud", label: "Fraud Monitor" },
  { to: "/customers", label: "Customers" },
  { to: "/premium", label: "Premium" },
];

export default function Header() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const links = !user ? GUEST_LINKS : isAdmin ? ADMIN_LINKS : CUSTOMER_LINKS;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="header">
      <Link to="/" className="brand">🏦 Simple Bank</Link>
      <nav className="nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            {link.label}
          </NavLink>
        ))}
        {user && (
          <>
            <span className="nav-user">
              {user.username ?? user.name}
              {isAdmin && <span className="badge">ADMIN</span>}
            </span>
            <button className="nav-link nav-button" onClick={handleLogout}>Log Out</button>
          </>
        )}
        <ThemeToggle />
      </nav>
    </header>
  );
}
