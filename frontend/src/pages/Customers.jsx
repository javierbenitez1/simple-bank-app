import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/dataService.js";
import CustomerTable from "../components/CustomerTable.jsx";
import SearchBar from "../components/SearchBar.jsx";
import Spinner from "../components/Spinner.jsx";

export default function Customers() {
  const [customers, setCustomers] = useState(null);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.listCustomers().then(setCustomers).catch((err) => setError(err.message));
  }, []);

  // Find customers by first name (the first word of their name)
  const term = search.trim().toLowerCase();
  const filtered = (customers ?? []).filter((c) =>
    c.name.split(" ")[0].toLowerCase().startsWith(term)
  );

  // Called by the child CustomerTable when Delete is clicked
  async function handleDelete(customer) {
    if (!window.confirm(`Delete ${customer.name}? This can't be undone.`)) return;
    setError("");
    setMessage("");
    try {
      await api.deleteCustomer(customer.userId);
      setCustomers((list) => list.filter((c) => c.userId !== customer.userId));
      setMessage(`Deleted ${customer.name}.`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h1>Customers</h1>
        <Link to="/customers/new" className="btn btn-primary">Add Customer</Link>
      </div>

      <SearchBar value={search} onSearch={setSearch} placeholder="Search by first name" />

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
      {!customers && !error && <Spinner message="Loading customers..." />}

      {customers && customers.length === 0 && (
        <p className="muted">No customers yet. Click Add Customer to create one.</p>
      )}
      {customers && customers.length > 0 && filtered.length === 0 && (
        <p className="muted">No customers with a first name starting with "{search}".</p>
      )}
      {filtered.length > 0 && (
        <CustomerTable
          customers={filtered}
          onView={(c) => navigate(`/customers/${c.userId}`)}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}
