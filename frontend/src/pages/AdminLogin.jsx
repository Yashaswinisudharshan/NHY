import { useState } from "react";
import axios from "axios";

export default function AdminLogin({ onLogin }) {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:8000/auth/login", form);
      if (res.data.error) {
        setError(res.data.error);
      } else {
        // Store token in memory and notify parent
        localStorage.setItem("admin_token", res.data.token);
        onLogin(res.data.token);
      }
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex", justifyContent: "center",
      alignItems: "center", minHeight: "80vh"
    }}>
      <div style={{
        background: "white", padding: "2rem",
        borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        width: "100%", maxWidth: "400px"
      }}>
        <h2 style={{ color: "#1565C0", marginTop: 0 }}>🔐 Admin Login</h2>
        <p style={{ color: "#666" }}>Only authorized admins can access this area.</p>

        <div style={{ marginBottom: "1rem" }}>
          <label style={labelStyle}>Username</label>
          <input
            style={inputStyle}
            placeholder="admin"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
          />
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <label style={labelStyle}>Password</label>
          <input
            style={inputStyle}
            type="password"
            placeholder="••••••••"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
          />
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: "100%", background: "#1565C0", color: "white",
            border: "none", padding: "0.75rem", borderRadius: "4px",
            fontSize: "1rem", cursor: "pointer"
          }}
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        {error && (
          <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#FFEBEE", borderRadius: "4px", color: "red" }}>
            ❌ {error}
          </div>
        )}

        <p style={{ marginTop: "1rem", color: "#999", fontSize: "0.85rem", textAlign: "center" }}>
          Default: admin / admin123
        </p>
      </div>
    </div>
  );
}

const labelStyle = { display: "block", marginBottom: "0.3rem", fontWeight: "bold", color: "#333" };
const inputStyle = { width: "100%", padding: "0.6rem", borderRadius: "4px", border: "1px solid #ccc", fontSize: "1rem", boxSizing: "border-box" };