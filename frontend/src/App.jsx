import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import BudgetRequest from "./pages/BudgetRequest";
import ComplaintForm from "./pages/ComplaintForm";
import ComplaintDashboard from "./pages/ComplaintDashboard";

export default function App() {
  const [page, setPage] = useState("dashboard");

  const navBtn = (id, label) => (
    <button
      onClick={() => setPage(id)}
      style={{
        background: page === id ? "white" : "transparent",
        color: page === id ? "#1565C0" : "white",
        border: "2px solid white",
        padding: "0.4rem 1rem",
        borderRadius: "4px",
        cursor: "pointer"
      }}
    >
      {label}
    </button>
  );

  return (
    <div style={{ fontFamily: "Arial, sans-serif" }}>
      <nav style={{
        padding: "1rem 2rem",
        background: "#1565C0",
        color: "white",
        display: "flex",
        alignItems: "center",
        gap: "1rem",
        flexWrap: "wrap"
      }}>
        <b style={{ fontSize: "1.1rem" }}>🏛️ Government AI System</b>
        {navBtn("dashboard", "📊 Budget Dashboard")}
        {navBtn("request", "📋 Budget Request")}
        {navBtn("complaint", "📝 File Complaint")}
        {navBtn("complaintDash", "🗂️ Complaint Dashboard")}
      </nav>

      {page === "dashboard" && <Dashboard />}
      {page === "request" && <BudgetRequest />}
      {page === "complaint" && <ComplaintForm />}
      {page === "complaintDash" && <ComplaintDashboard />}
    </div>
  );
}