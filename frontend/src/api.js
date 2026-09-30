const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Can't reach the bank server. Make sure the backend is running on port 8000.");
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    if (data?.detail) {
      message = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail;
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  return data;
}

const post = (path, body) => request(path, { method: "POST", body: JSON.stringify(body) });

export const api = {
  createUser: (name, email) => post("/api/users", { name, email }),
  listUsers: () => request("/api/users"),
  createAccount: (userId, accountType) => post("/api/accounts", { userId, accountType }),
  getAccount: (id) => request(`/api/accounts/${id}`),
  deposit: (id, amount) => post(`/api/accounts/${id}/deposit`, { amount }),
  withdraw: (id, amount) => post(`/api/accounts/${id}/withdraw`, { amount }),
  getTransactions: (id) => request(`/api/accounts/${id}/transactions`),
};

export const formatMoney = (n) =>
  Number(n).toLocaleString("en-US", { style: "currency", currency: "USD" });

// The API sends UTC times without a "Z", so add it to show the right local time
export const formatDate = (s) => {
  const hasZone = /Z|[+-]\d\d:\d\d$/.test(s);
  return new Date(hasZone ? s : `${s}Z`).toLocaleString();
};
