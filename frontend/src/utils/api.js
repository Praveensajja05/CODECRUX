import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:3001",
});

// Attach token to every request automatically
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const register = (data) => API.post("/api/auth/register", data);
export const login    = (data) => API.post("/api/auth/login", data);
export const getMe    = ()     => API.get("/api/auth/me");

// Profile
export const updateHandles = (data) => API.put("/api/profile/handles", data);

// Contests
export const getContests        = ()   => API.get("/api/contests");
export const refreshContests    = ()   => API.get("/api/contests/refresh");
export const setReminder        = (id) => API.post(`/api/contests/${id}/remind`);
export const removeReminder     = (id) => API.delete(`/api/contests/${id}/remind`);
export const getReminders       = ()   => API.get("/api/contests/reminders");

// Streak
export const getStreak  = ()     => API.get("/api/streak");
export const logActivity = (platform) => API.post("/api/streak/log", { platform });

// Submissions
export const submitCode = (data) => API.post("/api/submissions", data);

// Suggestions
export const getSuggestions = ()     => API.get("/api/suggestions");
export const analyzecode    = (data) => API.post("/api/suggestions/analyze", data);

// Calendar
export const getCalendarStatus = ()   => API.get("/api/calendar/status");
export const getCalendarAuthUrl = ()  => API.get("/api/calendar/auth");
export const addToCalendar      = (id) => API.post(`/api/calendar/add/${id}`);
export const removeFromCalendar = (id) => API.delete(`/api/calendar/remove/${id}`);
export const syncAllContests    = ()   => API.post("/api/calendar/sync-all");

// Dashboard
export const getDashboard = () => API.get("/api/dashboard");
export const getNotifications    = ()   => API.get("/api/notifications");
export const dismissNotification = (id) => API.put(`/api/notifications/${id}/dismiss`);
export const syncActivity        = ()   => API.post("/api/activity/sync");

export default API;
