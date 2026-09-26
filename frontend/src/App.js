import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";

function PrivateRoute({ children }) {
  const { student, loading } = useAuth();
  if (loading) return <div style={{ minHeight: "100vh", background: "#0f0f1a" }} />;
  return student ? children : <Navigate to="/" />;
}

function AppRoutes() {
  const { student } = useAuth();
  return (
    <Routes>
      <Route path="/" element={student ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      <Route path="/profile"   element={<PrivateRoute><Profile /></PrivateRoute>} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: "#1a1a2e", color: "white", border: "0.5px solid #2a2a3e" },
          }}
        />
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
