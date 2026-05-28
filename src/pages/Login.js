import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { login, register } from "../utils/api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [isLogin, setIsLogin]   = useState(true);
  const [loading, setLoading]   = useState(false);
  const [form, setForm]         = useState({ email: "", password: "", username: "" });
  const { loginUser }           = useAuth();
  const navigate                = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = isLogin
        ? await login({ email: form.email, password: form.password })
        : await register(form);

      loginUser(res.data.token, res.data.student);
      toast.success(isLogin ? "Welcome back!" : "Account created!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.error || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoMark}>cx</div>
          <span style={styles.logoText}>
            code<span style={{ color: "#7DF9C0" }}>crux</span>
          </span>
        </div>

        <p style={styles.tagline}>Your competitive programming tutor</p>

        {/* Toggle */}
        <div style={styles.toggle}>
          <button
            style={{ ...styles.toggleBtn, ...(isLogin ? styles.toggleActive : {}) }}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button
            style={{ ...styles.toggleBtn, ...(!isLogin ? styles.toggleActive : {}) }}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={styles.form}>
          {!isLogin && (
            <input
              style={styles.input}
              type="text"
              name="username"
              placeholder="Username"
              value={form.username}
              onChange={handleChange}
              required
            />
          )}
          <input
            style={styles.input}
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
          />
          <input
            style={styles.input}
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
          />
          <button style={styles.submitBtn} type="submit" disabled={loading}>
            {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
          </button>
        </form>

        <p style={styles.switchText}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span
            style={styles.switchLink}
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Register" : "Login"}
          </span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    background: "#0f0f1a",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
  },
  card: {
    background: "#1a1a2e",
    borderRadius: "16px",
    padding: "40px",
    width: "100%",
    maxWidth: "400px",
    border: "0.5px solid #2a2a3e",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    justifyContent: "center",
    marginBottom: "8px",
  },
  logoMark: {
    width: "36px",
    height: "36px",
    background: "#0f0f1a",
    borderRadius: "8px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "monospace",
    fontSize: "14px",
    fontWeight: "600",
    color: "#7DF9C0",
  },
  logoText: {
    fontSize: "22px",
    fontWeight: "700",
    color: "white",
    letterSpacing: "-0.5px",
  },
  tagline: {
    textAlign: "center",
    color: "#666",
    fontSize: "13px",
    marginBottom: "28px",
  },
  toggle: {
    display: "flex",
    background: "#0f0f1a",
    borderRadius: "8px",
    padding: "4px",
    marginBottom: "24px",
  },
  toggleBtn: {
    flex: 1,
    padding: "8px",
    border: "none",
    background: "transparent",
    color: "#666",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500",
  },
  toggleActive: {
    background: "#2a2a3e",
    color: "#7DF9C0",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  input: {
    padding: "12px 16px",
    background: "#0f0f1a",
    border: "0.5px solid #2a2a3e",
    borderRadius: "8px",
    color: "white",
    fontSize: "14px",
    outline: "none",
  },
  submitBtn: {
    padding: "12px",
    background: "#7DF9C0",
    border: "none",
    borderRadius: "8px",
    color: "#0f0f1a",
    fontSize: "14px",
    fontWeight: "700",
    cursor: "pointer",
    marginTop: "4px",
  },
  switchText: {
    textAlign: "center",
    color: "#666",
    fontSize: "13px",
    marginTop: "20px",
  },
  switchLink: {
    color: "#7DF9C0",
    cursor: "pointer",
  },
};
