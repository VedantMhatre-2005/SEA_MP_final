import { useState } from "react";
import { loginUser, registerUser } from "../services/api";

export default function AuthPanel({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [registerForm, setRegisterForm] = useState({ name: "", email: "", password: "" });
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });

  const startRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const res = await registerUser(registerForm);
      setMessage(res.message || "Registration successful. Please login.");
      setMode("login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const res = await loginUser(loginForm);
      localStorage.setItem("asprams_token", res.access_token);
      localStorage.setItem("asprams_user", JSON.stringify(res.user));
      onAuthenticated(res.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-6 sm:p-8 max-w-lg mx-auto">
      <h2 className="text-2xl font-bold text-slate-900 mb-2">Welcome to ASPRAMS</h2>
      <p className="text-sm text-slate-600 mb-6">Sign in to run analyses and view your history.</p>

      <div className="flex gap-2 mb-6">
        <button
          className={`px-4 py-2 rounded-lg text-sm font-semibold ${mode === "login" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"}`}
          onClick={() => {
            setMode("login");
            setError("");
            setMessage("");
          }}
          type="button"
        >
          Login
        </button>
        <button
          className={`px-4 py-2 rounded-lg text-sm font-semibold ${mode === "register" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"}`}
          onClick={() => {
            setMode("register");
            setError("");
            setMessage("");
          }}
          type="button"
        >
          Register
        </button>
      </div>

      {message && <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mb-3">{message}</p>}
      {error && <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2 mb-3">{error}</p>}

      {mode === "register" && (
        <form onSubmit={startRegister} className="space-y-3">
          <input className="form-input" placeholder="Full name" value={registerForm.name} onChange={(e) => setRegisterForm((p) => ({ ...p, name: e.target.value }))} />
          <input className="form-input" type="email" placeholder="Email" value={registerForm.email} onChange={(e) => setRegisterForm((p) => ({ ...p, email: e.target.value }))} />
          <input className="form-input" type="password" placeholder="Password (min 8 chars)" value={registerForm.password} onChange={(e) => setRegisterForm((p) => ({ ...p, password: e.target.value }))} />
          <button className="btn-primary w-full" disabled={loading} type="submit">{loading ? "Creating account..." : "Register"}</button>
        </form>
      )}

      {mode === "login" && (
        <form onSubmit={startLogin} className="space-y-3">
          <input className="form-input" type="email" placeholder="Email" value={loginForm.email} onChange={(e) => setLoginForm((p) => ({ ...p, email: e.target.value }))} />
          <input className="form-input" type="password" placeholder="Password" value={loginForm.password} onChange={(e) => setLoginForm((p) => ({ ...p, password: e.target.value }))} />
          <button className="btn-primary w-full" disabled={loading} type="submit">{loading ? "Signing in..." : "Login"}</button>
        </form>
      )}
    </div>
  );
}
