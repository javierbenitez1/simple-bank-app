import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import CreateAccount from "./pages/CreateAccount.jsx";
import AccountDetails from "./pages/AccountDetails.jsx";
import AmountForm from "./pages/AmountForm.jsx";
import Transactions from "./pages/Transactions.jsx";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="brand">🏦 Simple Bank</Link>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/create" element={<CreateAccount />} />
          <Route path="/accounts/:id" element={<AccountDetails />} />
          <Route path="/accounts/:id/deposit" element={<AmountForm key="deposit" mode="deposit" />} />
          <Route path="/accounts/:id/withdraw" element={<AmountForm key="withdraw" mode="withdraw" />} />
          <Route path="/accounts/:id/transactions" element={<Transactions />} />
          <Route
            path="*"
            element={
              <div className="card">
                <h1>Page not found</h1>
                <Link to="/" className="btn">Back to Home</Link>
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
