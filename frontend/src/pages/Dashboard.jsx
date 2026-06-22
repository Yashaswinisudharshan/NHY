import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend
} from "recharts";

export default function Dashboard() {
  const [allocations, setAllocations] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch both allocations and full history when page loads
    Promise.all([
      axios.get("http://localhost:8000/budget/allocations"),
      axios.get("http://localhost:8000/budget/history")
    ]).then(([allocRes, histRes]) => {
      setAllocations(allocRes.data);
      setHistory(histRes.data);
      setLoading(false);
    });
  }, []);

  // Format data for chart — show requested vs allocated
  const chartData = history.map((h, i) => ({
    name: h.department_name || `Request ${i + 1}`,
    Requested: h.requested,
    Allocated: h.allocated,
    Efficiency: h.efficiency_score ? Math.round(h.efficiency_score * 100) : 0
  }));

  if (loading) return (
    <div style={{ padding: "2rem" }}>Loading dashboard...</div>
  );

  return (
    <div style={{ padding: "2rem" }}>
      <h2 style={{ color: "#1565C0" }}>📊 Budget Allocation Dashboard</h2>

      {/* Summary Cards */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
        <div style={cardStyle("#E3F2FD")}>
          <h3>Total Requests</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold" }}>{history.length}</p>
        </div>
        <div style={cardStyle("#E8F5E9")}>
          <h3>Total Allocated</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold" }}>
            ₹{history.reduce((sum, h) => sum + (h.allocated || 0), 0).toLocaleString("en-IN")}
          </p>
        </div>
        <div style={cardStyle("#FFF3E0")}>
          <h3>Total Requested</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold" }}>
            ₹{history.reduce((sum, h) => sum + (h.requested || 0), 0).toLocaleString("en-IN")}
          </p>
        </div>
        <div style={cardStyle("#FCE4EC")}>
          <h3>Inflation Rate Used</h3>
          <p style={{ fontSize: "2rem", fontWeight: "bold" }}>
            {history[history.length - 1]?.inflation_rate || "N/A"}%
          </p>
        </div>
      </div>

      {/* Bar Chart */}
      <div style={{ background: "white", padding: "1rem", borderRadius: "8px", marginBottom: "2rem", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
        <h3>Requested vs Allocated (₹)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => `₹${value.toLocaleString("en-IN")}`} />
            <Legend />
            <Bar dataKey="Requested" fill="#90CAF9" />
            <Bar dataKey="Allocated" fill="#1565C0" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* History Table */}
      <div style={{ background: "white", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", overflow: "hidden" }}>
        <h3 style={{ padding: "1rem", margin: 0, borderBottom: "1px solid #eee" }}>
          Allocation History
        </h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "#1565C0", color: "white" }}>
            <tr>
              <th style={thStyle}>Department</th>
              <th style={thStyle}>Scheme</th>
              <th style={thStyle}>Requested</th>
              <th style={thStyle}>Allocated</th>
              <th style={thStyle}>Efficiency</th>
              <th style={thStyle}>Inflation %</th>
              <th style={thStyle}>AI Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? "#F5F5F5" : "white" }}>
                <td style={tdStyle}>{h.department_name || "-"}</td>
                <td style={tdStyle}>{h.scheme_name || "-"}</td>
                <td style={tdStyle}>₹{h.requested?.toLocaleString("en-IN")}</td>
                <td style={tdStyle}>₹{h.allocated?.toLocaleString("en-IN")}</td>
                <td style={tdStyle}>
                  <span style={{
                    background: h.efficiency_score >= 0.85 ? "#E8F5E9" : h.efficiency_score >= 0.6 ? "#FFF3E0" : "#FCE4EC",
                    padding: "2px 8px",
                    borderRadius: "12px",
                    color: h.efficiency_score >= 0.85 ? "green" : h.efficiency_score >= 0.6 ? "orange" : "red"
                  }}>
                    {h.efficiency_score ? Math.round(h.efficiency_score * 100) + "%" : "-"}
                  </span>
                </td>
                <td style={tdStyle}>{h.inflation_rate || "-"}%</td>
                <td style={{ ...tdStyle, fontSize: "0.75rem", maxWidth: "300px" }}>
                  {h.recommendation || "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const cardStyle = (bg) => ({
  background: bg,
  padding: "1rem 1.5rem",
  borderRadius: "8px",
  flex: 1,
  boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
});

const thStyle = {
  padding: "0.75rem 1rem",
  textAlign: "left"
};

const tdStyle = {
  padding: "0.75rem 1rem",
  borderBottom: "1px solid #eee"
};