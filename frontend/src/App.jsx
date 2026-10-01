import { Link, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import Header from "./components/Header.jsx";
import Footer from "./components/Footer.jsx";
import RequireAuth from "./components/RequireAuth.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import CustomerDashboard from "./pages/CustomerDashboard.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import Customers from "./pages/Customers.jsx";
import AddCustomer from "./pages/AddCustomer.jsx";
import CustomerDetails from "./pages/CustomerDetails.jsx";
import PremiumAccounts from "./pages/PremiumAccounts.jsx";
import CreateAccount from "./pages/CreateAccount.jsx";
import AccountDetails from "./pages/AccountDetails.jsx";
import AmountForm from "./pages/AmountForm.jsx";
import Transactions from "./pages/Transactions.jsx";
import Transfer from "./pages/Transfer.jsx";
import FraudMonitor from "./pages/FraudMonitor.jsx";

// "/" sends you to login, or to the right dashboard for your role
function HomeRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "ADMIN" ? "/admin" : "/dashboard"} replace />;
}

const protect = (page) => <RequireAuth>{page}</RequireAuth>;

export default function App() {
  return (
    <AuthProvider>
      <div className="app">
        <Header />
        <main className="container">
          <Routes>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/dashboard" element={protect(<CustomerDashboard />)} />
            <Route path="/admin" element={protect(<AdminDashboard />)} />
            <Route path="/customers" element={protect(<Customers />)} />
            <Route path="/customers/new" element={protect(<AddCustomer />)} />
            <Route path="/customers/:id" element={protect(<CustomerDetails />)} />
            <Route path="/premium" element={protect(<PremiumAccounts />)} />
            <Route path="/transfer" element={protect(<Transfer />)} />
            <Route path="/fraud" element={protect(<FraudMonitor />)} />
            <Route path="/create" element={protect(<CreateAccount />)} />
            <Route path="/accounts/:id" element={protect(<AccountDetails />)} />
            <Route path="/accounts/:id/deposit" element={protect(<AmountForm key="deposit" mode="deposit" />)} />
            <Route path="/accounts/:id/withdraw" element={protect(<AmountForm key="withdraw" mode="withdraw" />)} />
            <Route path="/accounts/:id/transactions" element={protect(<Transactions />)} />

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
    </AuthProvider>
  );
}
