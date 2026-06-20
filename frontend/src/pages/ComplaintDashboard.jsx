import { useEffect, useState, useRef } from "react";
import axios from "axios";
import AdminLogin from "./AdminLogin";

const STAGES = ["Submitted", "Under Review", "In Progress", "Resolved"];
const STATUS_COLORS = {
  "Submitted": "#FFF3E0", "Under Review": "#E3F2FD",
  "In Progress": "#F3E5F5", "Resolved": "#E8F5E9"
};
const STATUS_TEXT_COLORS = {
  "Submitted": "orange", "Under Review": "#1565C0",
  "In Progress": "purple", "Resolved": "green"
};

export default function ComplaintDashboard() {
  const [token, setToken] = useState(localStorage.getItem("admin_token"));
  const [complaints, setComplaints] = useState([]);
  const [stats, setStats] = useState(null);
  const [trackId, setTrackId] = useState("");
  const [tracked, setTracked] = useState(null);
  const [loading, setLoading] = useState(false);

  const authHeaders = { Authorization: `Bearer ${token}` };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [compRes, statsRes] = await Promise.all([
        axios.get("http://localhost:8000/complaints/all", { headers: authHeaders }),
        axios.get("http://localhost:8000/complaints/stats", { headers: authHeaders })
      ]);
      setComplaints(Array.isArray(compRes.data) ? compRes.data : []);
      setStats(statsRes.data.total !== undefined ? statsRes.data : null);
    } catch {
      setToken(null);
      localStorage.removeItem("admin_token");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (token) fetchData();
  }, [token]);

  const handleTrack = async () => {
    if (!trackId) return;
    const res = await axios.get(`http://localhost:8000/complaints/track/${trackId}`);
    setTracked(res.data);
  };

  const handleUpdateStage = async (complaint_id, stage) => {
    await axios.put(
      `http://localhost:8000/complaints/update-stage/${complaint_id}?stage=${stage}`,
      {},
      { headers: authHeaders }
    );
    fetchData();
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setToken(null);
  };

  if (!token) return <AdminLogin onLogin={setToken} />;
  if (loading) return <div style={{ padding: "2rem" }}>Loading...</div>;

  return (
    <div style={{ padding: "2rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ color: "#1565C0", margin: 0 }}>🗂️ Admin — Complaint Dashboard</h2>
        <button
          onClick={handleLogout}
          style={{ background: "#EF5350", color: "white", border: "none", padding: "0.5rem 1rem", borderRadius: "4px", cursor: "pointer" }}
        >
          Logout
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
          <div style={cardStyle("#E3F2FD")}>
            <h3>Total</h3>
            <p style={bigNum}>{stats.total}</p>
          </div>
          {STAGES.map(stage => (
            <div key={stage} style={cardStyle(STATUS_COLORS[stage])}>
              <h3>{stage}</h3>
              <p style={{ ...bigNum, color: STATUS_TEXT_COLORS[stage] }}>
                {stats.by_status?.[stage] || 0}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Track */}
      <div style={{ background: "white", padding: "1.5rem", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", marginBottom: "2rem" }}>
        <h3 style={{ marginTop: 0 }}>🔍 Track a Complaint</h3>
        <div style={{ display: "flex", gap: "1rem" }}>
          <input
            style={{ flex: 1, padding: "0.6rem", borderRadius: "4px", border: "1px solid #ccc" }}
            placeholder="e.g. CMP-2025-A3F7B2"
            value={trackId}
            onChange={e => setTrackId(e.target.value)}
          />
          <button
            onClick={handleTrack}
            style={{ background: "#1565C0", color: "white", border: "none", padding: "0.6rem 1.5rem", borderRadius: "4px", cursor: "pointer" }}
          >
            Track
          </button>
        </div>

        {tracked && !tracked.error && (
          <div style={{ marginTop: "1rem", padding: "1rem", background: "#F5F5F5", borderRadius: "8px" }}>
            <p><b>ID:</b> {tracked.complaint_id}</p>
            <p><b>Category:</b> {tracked.category}</p>
            <p><b>Department:</b> {tracked.assigned_department}</p>
            <p><b>Location:</b> {tracked.location}</p>
            <p><b>Status:</b> <span style={{ color: STATUS_TEXT_COLORS[tracked.status], fontWeight: "bold" }}>{tracked.status}</span></p>
            <h4>Stage History:</h4>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {tracked.stage_history?.map((s, i) => (
                <div key={i} style={{ background: "white", padding: "0.5rem 1rem", borderRadius: "20px", border: "2px solid #1565C0", fontSize: "0.85rem" }}>
                  ✅ {s.stage}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div style={{ background: "white", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)", overflow: "auto" }}>
        <h3 style={{ padding: "1rem", margin: 0, borderBottom: "1px solid #eee" }}>All Complaints</h3>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "#1565C0", color: "white" }}>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Citizen</th>
              <th style={thStyle}>Location</th>
              <th style={thStyle}>Category</th>
              <th style={thStyle}>Department</th>
              <th style={thStyle}>Language</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Update Stage</th>
            </tr>
          </thead>
          <tbody>
            {complaints.map((c, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? "#F5F5F5" : "white" }}>
                <td style={tdStyle}><small>{c.complaint_id}</small></td>
                <td style={tdStyle}>{c.citizen_name}</td>
                <td style={tdStyle}>{c.location}</td>
                <td style={tdStyle}>{c.category}</td>
                <td style={tdStyle}>{c.assigned_department}</td>
                <td style={tdStyle}>{c.detected_language?.toUpperCase()}</td>
                <td style={tdStyle}>
                  <span style={{
                    background: STATUS_COLORS[c.status],
                    color: STATUS_TEXT_COLORS[c.status],
                    padding: "2px 8px", borderRadius: "12px",
                    fontWeight: "bold", fontSize: "0.85rem"
                  }}>
                    {c.status}
                  </span>
                </td>
                <td style={tdStyle}>
                  <select
                    value={c.status}
                    onChange={e => handleUpdateStage(c.complaint_id, e.target.value)}
                    style={{ padding: "0.3rem", borderRadius: "4px", border: "1px solid #ccc" }}
                  >
                    {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const cardStyle = (bg) => ({ background: bg, padding: "1rem 1.5rem", borderRadius: "8px", minWidth: "120px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" });
const bigNum = { fontSize: "2rem", fontWeight: "bold", margin: 0 };
const thStyle = { padding: "0.75rem 1rem", textAlign: "left" };
const tdStyle = { padding: "0.75rem 1rem", borderBottom: "1px solid #eee" };