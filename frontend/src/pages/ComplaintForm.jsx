import { useState, useRef } from "react";
import axios from "axios";

export default function ComplaintForm() {
  const [form, setForm] = useState({
    citizen_name: "", location: "", description: ""
  });
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const startVoice = () => {
    /**
     * Web Speech API — built into Chrome/Edge browsers.
     * No library needed, no API key, completely free.
     * 
     * How it works:
     * - Browser listens to microphone
     * - Converts speech to text in real time
     * - We get the transcript and put it in the description field
     * 
     * Why is this useful for complaints?
     * Many citizens (especially elderly or rural) find typing hard.
     * Speaking is much more natural and accessible.
     */
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input not supported in this browser. Please use Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "ta-IN";       // Tamil — change to "hi-IN" for Hindi, "en-IN" for English
    recognition.interimResults = false; // only final results
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      // Append to existing description instead of replacing
      setForm(prev => ({
        ...prev,
        description: prev.description
          ? prev.description + " " + transcript
          : transcript
      }));
    };

    recognition.onerror = (e) => {
      console.error("Voice error:", e);
      setListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopVoice = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  const handleSubmit = async () => {
    if (!form.citizen_name || !form.location || !form.description) {
      setError("Please fill in all required fields");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("citizen_name", form.citizen_name);
      formData.append("location", form.location);
      formData.append("description", form.description);
      if (image) formData.append("image", image);

      const res = await axios.post(
        "http://localhost:8000/complaints/submit",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setResult(res.data);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px" }}>
      <h2 style={{ color: "#1565C0" }}>📝 Submit a Complaint</h2>
      <p style={{ color: "#666" }}>Write in any language — Tamil, Hindi, Telugu, English.</p>

      <div style={fieldStyle}>
        <label style={labelStyle}>Your Name *</label>
        <input style={inputStyle} placeholder="Enter your name"
          value={form.citizen_name}
          onChange={e => setForm({ ...form, citizen_name: e.target.value })} />
      </div>

      <div style={fieldStyle}>
        <label style={labelStyle}>Location *</label>
        <input style={inputStyle} placeholder="e.g. Anna Nagar, Chennai"
          value={form.location}
          onChange={e => setForm({ ...form, location: e.target.value })} />
      </div>

      <div style={fieldStyle}>
        <label style={labelStyle}>Describe the Problem * (any language)</label>
        <textarea
          style={{ ...inputStyle, height: "120px", resize: "vertical" }}
          placeholder="சாலையில் பள்ளம் உள்ளது / यहाँ कचरा है / There is a pothole..."
          value={form.description}
          onChange={e => setForm({ ...form, description: e.target.value })}
        />

        {/* Voice Button */}
        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <button
            onClick={listening ? stopVoice : startVoice}
            style={{
              background: listening ? "#EF5350" : "#43A047",
              color: "white", border: "none",
              padding: "0.5rem 1rem", borderRadius: "4px",
              cursor: "pointer", display: "flex",
              alignItems: "center", gap: "0.4rem"
            }}
          >
            {listening ? "🔴 Stop Recording" : "🎤 Speak your complaint"}
          </button>
          {listening && (
            <span style={{ color: "#EF5350", fontWeight: "bold", animation: "pulse 1s infinite" }}>
              Listening...
            </span>
          )}
        </div>
        <small style={{ color: "#666" }}>
          🎤 Works in Tamil, Hindi, English. Click mic and speak clearly.
        </small>
      </div>

      <div style={fieldStyle}>
        <label style={labelStyle}>Upload Photo (optional)</label>
        <input type="file" accept="image/*"
          onChange={e => setImage(e.target.files[0])}
          style={{ padding: "0.5rem 0" }} />
        {image && (
          <img src={URL.createObjectURL(image)} alt="preview"
            style={{ width: "100%", maxHeight: "200px", objectFit: "cover", borderRadius: "8px", marginTop: "0.5rem" }} />
        )}
      </div>

      <button onClick={handleSubmit} disabled={loading} style={{
        background: loading ? "#90CAF9" : "#1565C0", color: "white",
        border: "none", padding: "0.75rem 2rem", borderRadius: "4px",
        fontSize: "1rem", cursor: loading ? "not-allowed" : "pointer"
      }}>
        {loading ? "Submitting..." : "Submit Complaint"}
      </button>

      {error && (
        <div style={{ marginTop: "1rem", padding: "1rem", background: "#FFEBEE", borderRadius: "8px", borderLeft: "4px solid red" }}>
          ❌ {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: "1.5rem", padding: "1.5rem", background: "#E8F5E9", borderRadius: "8px", borderLeft: "4px solid green" }}>
          <h3 style={{ color: "green", marginTop: 0 }}>✅ Complaint Registered!</h3>
          <div style={{ background: "white", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
            <p><b>Complaint ID:</b> <span style={{ fontSize: "1.2rem", color: "#1565C0" }}>{result.complaint_id}</span></p>
            <p style={{ color: "#666", fontSize: "0.85rem" }}>Save this ID to track your complaint</p>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div style={resultCard}><small>Category</small><b>{result.category}</b></div>
            <div style={resultCard}><small>Assigned To</small><b>{result.assigned_to}</b></div>
            <div style={resultCard}><small>Status</small><b style={{ color: "green" }}>{result.status}</b></div>
            <div style={resultCard}><small>Language Detected</small><b>{result.translation?.detected_language?.toUpperCase()}</b></div>
          </div>
          {result.translation?.detected_language !== "en" && (
            <div style={{ marginTop: "1rem", background: "#E3F2FD", padding: "1rem", borderRadius: "8px" }}>
              <b>🌐 Translation</b>
              <p style={{ margin: "0.5rem 0 0 0" }}>{result.translation?.translated_text}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const fieldStyle = { marginBottom: "1rem" };
const labelStyle = { display: "block", marginBottom: "0.3rem", fontWeight: "bold", color: "#333" };
const inputStyle = { width: "100%", padding: "0.6rem", borderRadius: "4px", border: "1px solid #ccc", fontSize: "1rem", boxSizing: "border-box" };
const resultCard = { background: "white", padding: "0.75rem", borderRadius: "4px", display: "flex", flexDirection: "column", gap: "0.2rem" };
