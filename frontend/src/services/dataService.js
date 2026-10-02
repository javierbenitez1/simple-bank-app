// Data Service: every call to the backend REST API goes through here
// Uses the live API when built for AWS, and your local server otherwise
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
const SESSION_KEY = "simpleBankSession";

// ----- Session (token + logged-in user), saved so a refresh keeps you logged in -----
export function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}
export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}
export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

// Called when the server says our token is missing, invalid, or expired
let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

async function request(path, options = {}) {
  const token = loadSession()?.token;
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error("Can't reach the bank server. Make sure the backend is running on port 8000.");
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401 && token && !path.startsWith("/api/auth/login")) onUnauthorized();
    let message = "Something went wrong. Please try again.";
    if (data?.detail) {
      message = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join(", ") : data.detail;
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  return data;
}

const post = (path, body) => request(path, { method: "POST", body: JSON.stringify(body) });
const remove = (path) => request(path, { method: "DELETE" });

export const api = {
  // Auth
  login: (username, password) => post("/api/auth/login", { username, password }),
  register: (customer) => post("/api/users", customer),
  me: () => request("/api/auth/me"),

  // Dashboards
  getAdminDashboard: () => request("/api/admin"),
  getCustomerDashboard: (id) => request(`/api/customerDashboard/${id}`),

  // Customers
  listCustomers: () => request("/api/users"),
  getCustomer: (id) => request(`/api/users/${id}`),
  deleteCustomer: (id) => remove(`/api/users/${id}`),
  getCustomerAccounts: (id) => request(`/api/users/${id}/accounts`),

  // Accounts
  createAccount: (userId, accountType) => post("/api/accounts", { userId, accountType }),
  getAccount: (id) => request(`/api/accounts/${id}`),
  getPremiumAccounts: (threshold) =>
    request(`/api/accounts/premium?threshold=${encodeURIComponent(threshold)}`),
  deposit: (id, amount) => post(`/api/accounts/${id}/deposit`, { amount }),
  withdraw: (id, amount) => post(`/api/accounts/${id}/withdraw`, { amount }),
  getTransactions: (id) => request(`/api/accounts/${id}/transactions`),
  transfer: (fromAccountId, toAccountId, amount) =>
    post("/api/accounts/transfer", { fromAccountId, toAccountId, amount }),

  // Audit log (admin only). Empty filters are skipped.
  getAuditLogs: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== "" && value != null) params.set(key, value);
    });
    const query = params.toString();
    return request(`/api/audit${query ? `?${query}` : ""}`);
  },
};

export const formatMoney = (n) =>
  Number(n).toLocaleString("en-US", { style: "currency", currency: "USD" });

// The API sends UTC times without a "Z", so add it to show the right local time
export const formatDate = (s) => {
  const hasZone = /Z|[+-]\d\d:\d\d$/.test(s);
  return new Date(hasZone ? s : `${s}Z`).toLocaleString();
};
