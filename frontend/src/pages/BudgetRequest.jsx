import { useState, useEffect } from "react";
import axios from "axios";

export default function BudgetRequest() {
  const [schemes, setSchemes] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState({
    department_id: "",
    requested_amount: "",
    fiscal_year: 2025,
    amount_allocated_last_year: "",
    amount_utilized_last_year: "",
    justification: "",
    scheme_name: ""
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch schemes and departments when page loads
    axios.get("http://localhost:8000/budget/schemes")
      .then(res => setSchemes(res.data.schemes));
    axios.get("http://localhost:8000/departments/")
      .then(res => setDepartments(res.data));
  }, []);

  const handleSubmit = async () => {
    // Basic frontend validation
    if (!form.department_id || !form.requested_amount || !form.justification || !form.scheme_name) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await axios.post("http://localhost:8000/budget/request", {
        department_id: parseInt(form.department_id),
        requested_amount: parseFloat(form.requested_amount),
        fiscal_year: parseInt(form.fiscal_year),
        amount_allocated_last_year: parseFloat(form.amount_allocated_last_year) || 0,
        amount_utilized_last_year: parseFloat(form.amount_utilized_last_year) || 0,
        justification: form.justification,
        scheme_name: form.scheme_name
      });

      if (res.data.error) {
        setError(res.data.reason || res.data.error);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "700px" }}>
      <h2 style={{ color: "#1565C0" }}>📋 Submit Budget Request</h2>

      {/* Department Dropdown */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Department *</label>
        <select
          style={inputStyle}
          value={form.department_id}
          onChange={e => setForm({ ...form, department_id: e.target.value })}
        >
          <option value="">Select Department</option>
          {departments.map(d => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
      </div>

      {/* Scheme Dropdown */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Government Scheme *</label>
        <select
          style={inputStyle}
          value={form.scheme_name}
          onChange={e => setForm({ ...form, scheme_name: e.target.value })}
        >
          <option value="">Select Scheme</option>
          {schemes.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Requested Amount */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Requested Amount (₹) *</label>
        <input
          style={inputStyle}
          type="number"
          placeholder="e.g. 1000000"
          value={form.requested_amount}
          onChange={e => setForm({ ...form, requested_amount: e.target.value })}
        />
      </div>

      {/* Last Year Allocated */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Amount Allocated Last Year (₹)</label>
        <input
          style={inputStyle}
          type="number"
          placeholder="e.g. 900000"
          value={form.amount_allocated_last_year}
          onChange={e => setForm({ ...form, amount_allocated_last_year: e.target.value })}
        />
      </div>

      {/* Last Year Utilized */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Amount Utilized Last Year (₹)</label>
        <input
          style={inputStyle}
          type="number"
          placeholder="e.g. 855000"
          value={form.amount_utilized_last_year}
          onChange={e => setForm({ ...form, amount_utilized_last_year: e.target.value })}
        />
      </div>

      {/* Fiscal Year */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Fiscal Year *</label>
        <input
          style={inputStyle}
          type="number"
          value={form.fiscal_year}
          onChange={e => setForm({ ...form, fiscal_year: e.target.value })}
        />
      </div>

      {/* Justification */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Justification * (be specific!)</label>
        <textarea
          style={{ ...inputStyle, height: "100px", resize: "vertical" }}
          placeholder="e.g. Expanding 3 primary healthcare centers in rural Krishnagiri district serving 15000 beneficiaries"
          value={form.justification}
          onChange={e => setForm({ ...form, justification: e.target.value })}
        />
        <small style={{ color: "#666" }}>
          Tip: Include specific locations, numbers, and objectives. Vague justifications will be rejected by AI.
        </small>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          background: loading ? "#90CAF9" : "#1565C0",
          color: "white",
          border: "none",
          padding: "0.75rem 2rem",
          borderRadius: "4px",
          fontSize: "1rem",
          cursor: loading ? "not-allowed" : "pointer",
          marginTop: "1rem"
        }}
      >
        {loading ? "Processing..." : "Submit Request"}
      </button>

      {/* Error Message */}
      {error && (
        <div style={{
          marginTop: "1.5rem",
          padding: "1rem",
          background: "#FFEBEE",
          borderRadius: "8px",
          borderLeft: "4px solid red"
        }}>
          <b>❌ Request Rejected</b>
          <p>{error}</p>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div style={{
          marginTop: "1.5rem",
          padding: "1.5rem",
          background: "#E8F5E9",
          borderRadius: "8px",
          borderLeft: "4px solid green"
        }}>
          <h3 style={{ color: "green", marginTop: 0 }}>✅ Request Approved</h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
            <div style={resultCardStyle}>
              <small>Department</small>
              <b>{result.department}</b>
            </div>
            <div style={resultCardStyle}>
              <small>Scheme</small>
              <b>{result.scheme}</b>
            </div>
            <div style={resultCardStyle}>
              <small>Requested</small>
              <b>₹{result.requested?.toLocaleString("en-IN")}</b>
            </div>
            <div style={resultCardStyle}>
              <small>Allocated</small>
              <b style={{ color: "#1565C0", fontSize: "1.2rem" }}>
                ₹{result.allocated?.toLocaleString("en-IN")}
              </b>
            </div>
            <div style={resultCardStyle}>
              <small>Inflation Rate Used</small>
              <b>{result.inflation_rate_used}%</b>
            </div>
            <div style={resultCardStyle}>
              <small>Efficiency Score</small>
              <b>{Math.round(result.factors?.efficiency_score * 100)}%</b>
            </div>
          </div>

          {/* Breakdown */}
          <div style={{ background: "white", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
            <b>📊 Allocation Breakdown</b>
            <table style={{ width: "100%", marginTop: "0.5rem", borderCollapse: "collapse" }}>
              <tbody>
                <tr>
                  <td style={bdTd}>Step 1 — Requested Amount</td>
                  <td style={bdTd}>₹{result.breakdown?.step1_requested?.toLocaleString("en-IN")}</td>
                </tr>
                <tr style={{ background: "#F5F5F5" }}>
                  <td style={bdTd}>Step 2 — After Inflation Adjustment ({result.inflation_rate_used}%)</td>
                  <td style={bdTd}>₹{result.breakdown?.step2_after_inflation?.toLocaleString("en-IN")}</td>
                </tr>
                <tr>
                  <td style={bdTd}>Step 3 — After Efficiency Score ({Math.round(result.factors?.efficiency_score * 100)}%)</td>
                  <td style={bdTd}>₹{result.breakdown?.step3_after_efficiency?.toLocaleString("en-IN")}</td>
                </tr>
                <tr style={{ background: "#F5F5F5" }}>
                  <td style={bdTd}>Step 4 — After Priority Weight ({result.factors?.priority_weight})</td>
                  <td style={bdTd}><b>₹{result.breakdown?.step4_after_priority?.toLocaleString("en-IN")}</b></td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* AI Recommendation */}
          <div style={{ background: "#E3F2FD", padding: "1rem", borderRadius: "8px" }}>
            <b>🤖 AI Policy Recommendation</b>
            <p style={{ margin: "0.5rem 0 0 0", lineHeight: "1.6" }}>
              {result.ai_recommendation}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

const fieldStyle = { marginBottom: "1rem" };
const labelStyle = { display: "block", marginBottom: "0.3rem", fontWeight: "bold", color: "#333" };
const inputStyle = { width: "100%", padding: "0.6rem", borderRadius: "4px", border: "1px solid #ccc", fontSize: "1rem", boxSizing: "border-box" };
const resultCardStyle = { background: "white", padding: "0.75rem", borderRadius: "4px", display: "flex", flexDirection: "column", gap: "0.2rem" };
const bdTd = { padding: "0.5rem", borderBottom: "1px solid #eee" };