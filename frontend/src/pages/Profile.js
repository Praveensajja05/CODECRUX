import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { getMe, updateHandles } from "../utils/api";

export default function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    leetcode_handle:   "",
    codeforces_handle: "",
    codechef_handle:   "",
    atcoder_handle:    "",
  });

  useEffect(() => {
    getMe().then(res => {
      setForm({
        leetcode_handle:   res.data.leetcode_handle   || "",
        codeforces_handle: res.data.codeforces_handle || "",
        codechef_handle:   res.data.codechef_handle   || "",
        atcoder_handle:    res.data.atcoder_handle    || "",
      });
    });
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateHandles(form);
      toast.success("Handles updated successfully");
      navigate("/dashboard");
    } catch (err) {
      toast.error("Failed to update handles");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <button style={styles.backBtn} onClick={() => navigate("/dashboard")}>← Back</button>
          <h2 style={styles.title}>Platform Handles</h2>
        </div>
        <p style={styles.subtitle}>Enter your username only, not the full URL. Example: for leetcode.com/u/john, enter just "john".</p>

        <form onSubmit={handleSave} style={styles.form}>
          {[
            { name: "leetcode_handle",   label: "LeetCode",   placeholder: "your-leetcode-username",   color: "#f97316" },
            { name: "codeforces_handle", label: "Codeforces", placeholder: "your-codeforces-handle",   color: "#3b82f6" },
            { name: "codechef_handle",   label: "CodeChef",   placeholder: "your-codechef-username",   color: "#8b5cf6" },
            { name: "atcoder_handle",    label: "AtCoder",    placeholder: "your-atcoder-username",    color: "#10b981" },
          ].map(field => (
            <div key={field.name} style={styles.field}>
              <label style={{ ...styles.label, color: field.color }}>{field.label}</label>
              <input
                style={styles.input}
                type="text"
                name={field.name}
                placeholder={field.placeholder}
                value={form[field.name]}
                onChange={handleChange}
              />
            </div>
          ))}

          <button style={styles.saveBtn} type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save Handles"}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: "100vh", background: "#0f0f1a", display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" },
  card: { background: "#1a1a2e", borderRadius: "16px", padding: "32px", width: "100%", maxWidth: "480px", border: "0.5px solid #2a2a3e" },
  header: { display: "flex", alignItems: "center", gap: "16px", marginBottom: "8px" },
  backBtn: { background: "transparent", border: "none", color: "#666", cursor: "pointer", fontSize: "13px" },
  title: { fontSize: "18px", fontWeight: "700", color: "white", margin: 0 },
  subtitle: { fontSize: "13px", color: "#444", marginBottom: "24px" },
  form: { display: "flex", flexDirection: "column", gap: "16px" },
  field: { display: "flex", flexDirection: "column", gap: "6px" },
  label: { fontSize: "12px", fontWeight: "600", letterSpacing: "0.5px" },
  input: { padding: "10px 14px", background: "#0f0f1a", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "white", fontSize: "13px", outline: "none", fontFamily: "monospace" },
  saveBtn: { padding: "12px", background: "#7DF9C0", border: "none", borderRadius: "8px", color: "#0f0f1a", fontSize: "14px", fontWeight: "700", cursor: "pointer", marginTop: "8px" },
};
