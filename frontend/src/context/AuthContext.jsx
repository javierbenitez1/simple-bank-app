import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, clearSession, loadSession, saveSession, setUnauthorizedHandler } from "../services/dataService.js";

// Shares who is logged in with every component, without passing props through every level
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => loadSession()); // { token, user } or null

  const logout = useCallback(() => {
    clearSession();
    setSession(null);
  }, []);

  // If the server rejects our token (expired or invalid), log out automatically
  useEffect(() => {
    setUnauthorizedHandler(logout);
  }, [logout]);

  async function login(username, password) {
    const data = await api.login(username, password);
    const next = { token: data.accessToken, user: data.user };
    saveSession(next);
    setSession(next);
    return data.user;
  }

  async function register({ name, email, username, password }) {
    await api.register({ name, email, username, password });
    return login(username, password);
  }

  const user = session?.user ?? null;
  const value = { user, isAdmin: user?.role === "ADMIN", login, register, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
