import React, { createContext, useContext, useState, useEffect } from "react";
import { getMe } from "../utils/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getMe()
        .then((res) => setStudent(res.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const loginUser = (token, studentData) => {
    localStorage.setItem("token", token);
    setStudent(studentData);
  };

  const logoutUser = () => {
    localStorage.removeItem("token");
    setStudent(null);
  };

  return (
    <AuthContext.Provider value={{ student, loading, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
