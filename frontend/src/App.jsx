import { Link, Route, Routes } from "react-router-dom";
import Header from "./components/Header.jsx";
import Footer from "./components/Footer.jsx";
import Home from "./pages/Home.jsx";
import Customers from "./pages/Customers.jsx";
import AddCustomer from "./pages/AddCustomer.jsx";
import CustomerDetails from "./pages/CustomerDetails.jsx";
import PremiumAccounts from "./pages/PremiumAccounts.jsx";
import CreateAccount from "./pages/CreateAccount.jsx";
import AccountDetails from "./pages/AccountDetails.jsx";
import AmountForm from "./pages/AmountForm.jsx";
import Transactions from "./pages/Transactions.jsx";

// App is the parent: Header, the current page, and Footer are its children
export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/new" element={<AddCustomer />} />
          <Route path="/customers/:id" element={<CustomerDetails />} />
          <Route path="/premium" element={<PremiumAccounts />} />
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
      <Footer />
    </div>
  );
}
