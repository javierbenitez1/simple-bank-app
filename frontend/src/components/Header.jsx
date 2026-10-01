import { Link, NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/customers", label: "Customers" },
  { to: "/premium", label: "Premium" },
  { to: "/create", label: "Open Account" },
];

export default function Header() {
  return (
    <header className="header">
      <Link to="/" className="brand">🏦 Simple Bank</Link>
      <nav className="nav">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
