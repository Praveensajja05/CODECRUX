import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import { getDashboard, getContests, setReminder, removeReminder, getCalendarStatus, getCalendarAuthUrl, addToCalendar, getSuggestions, getNotifications, dismissNotification, syncActivity } from "../utils/api";
import StreakCard from "../components/dashboard/StreakCard";
import ContestCard from "../components/contests/ContestCard";
import SuggestionsPanel from "../components/suggestions/SuggestionsPanel";

export default function Dashboard() {
  const { student, logoutUser } = useAuth();
  const navigate                = useNavigate();
  const [activeTab, setActiveTab]         = useState("contests");
  const [dashboard, setDashboard]         = useState(null);
  const [contests, setContests]           = useState([]);
  const [suggestions, setSuggestions]     = useState(null);
  const [calendarConnected, setCalendar]  = useState(false);
  const [reminders, setReminders]         = useState({});
  const [notification , setNotifications ]=useState([]);
  const [loading, setLoading]             = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    if (activeTab === "suggestions") loadSuggestions();
  }, [activeTab]);

  async function loadDashboard() {
    try {
      const [dashRes, contestRes, calRes] = await Promise.all([
        getDashboard(),
        getContests(),
        getCalendarStatus(),
      ]);
      setDashboard(dashRes.data);
     const sorted = (contestRes.data.contests || []).sort(
  (a, b) => new Date(a.start_time) - new Date(b.start_time)
);
setContests(sorted);
      setCalendar(calRes.data.connected);
      try {
  const notifRes = await getNotifications();
  setNotifications(notifRes.data.notifications || []);
} catch {}
    } catch (err) {
      toast.error("Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  async function loadSuggestions() {
    try {
      const res = await getSuggestions();
      setSuggestions(res.data);
    } catch (err) {
      console.log("No suggestions yet");
    }
  }

  async function handleReminder(contestId) {
    try {
      if (reminders[contestId]) {
        await removeReminder(contestId);
        setReminders(prev => ({ ...prev, [contestId]: false }));
        toast.success("Reminder removed");
      } else {
        await setReminder(contestId);
        setReminders(prev => ({ ...prev, [contestId]: true }));
        toast.success("Reminder set for 30 min before contest");
      }
    } catch (err) {
      toast.error("Failed to set reminder");
    }
  }

  async function handleCalendarConnect() {
    try {
      const res = await getCalendarAuthUrl();
      window.open(res.data.url, "_blank", "width=500,height=600");
      setTimeout(() => {
        getCalendarStatus().then(r => setCalendar(r.data.connected));
      }, 5000);
    } catch (err) {
      toast.error("Failed to connect calendar");
    }
  }

  async function handleAddToCalendar(contestId) {
    try {
      await addToCalendar(contestId);
      toast.success("Added to Google Calendar with 30 min reminder");
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to add to calendar");
    }
  }

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.loadingText}>Loading CodeCrux...</div>
      </div>
    );
  }

  return (
    <div style={styles.root}>
      {/* Topbar */}
      <div style={styles.topbar}>
        <div style={styles.logo}>
          <div style={styles.logoMark}>cx</div>
          <span style={styles.logoText}>
            code<span style={{ color: "#7DF9C0" }}>crux</span>
          </span>
        </div>
        <div style={styles.nav}>
          {["contests", "suggestions", "progress"].map(tab => (
            <button
              key={tab}
              style={{ ...styles.navBtn, ...(activeTab === tab ? styles.navActive : {}) }}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
        <div style={styles.topRight}>
          <span style={styles.username}>{student?.username}</span>
          <button style={styles.logoutBtn} onClick={() => { logoutUser(); navigate("/"); }}>
            Logout
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={styles.body}>
        {/* Sidebar */}
        <aside style={styles.sidebar}>
          <StreakCard streak={dashboard?.streak} />

          <div style={styles.sideSection}>
            <div style={styles.sectionLabel}>Platforms</div>
            {[
              { name: "LeetCode",   handle: dashboard?.profile?.leetcode_handle,   color: "#f97316" },
              { name: "Codeforces", handle: dashboard?.profile?.codeforces_handle, color: "#3b82f6" },
              { name: "CodeChef",   handle: dashboard?.profile?.codechef_handle,   color: "#8b5cf6" },
              { name: "AtCoder",    handle: dashboard?.profile?.atcoder_handle,    color: "#10b981" },
            ].map(p => (
              <div key={p.name} style={styles.platformRow}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{ ...styles.platformDot, background: p.color }} />
                  <span style={styles.platformName}>{p.name}</span>
                </div>
                <span style={styles.platformHandle} title={p.handle}>
  {p.handle ? (p.handle.length > 12 ? p.handle.slice(0, 12) + "..." : p.handle) : "not set"}
</span>
              </div>
            ))}
            <button style={styles.editBtn} onClick={() => navigate("/profile")}>
              Edit Handles
            </button>
          </div>

          <div style={styles.sideSection}>
            <div style={styles.sectionLabel}>Google Calendar</div>
            <button
              style={{ ...styles.calBtn, ...(calendarConnected ? styles.calConnected : {}) }}
              onClick={calendarConnected ? null : handleCalendarConnect}
            >
              {calendarConnected ? "✓ Synced with Google" : "Connect Google Calendar"}
            </button>
            {calendarConnected && (
              <p style={styles.calNote}>Contests auto-added. 30 min reminders on.</p>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <main style={styles.main}>
        {notification.filter(n => !n.seen).length > 0 && (
  <div style={styles.notifBanner}>
    {notification.filter(n => !n.seen).map(n => (
      <div key={n.id} style={styles.notifItem}>
        <div style={styles.notifLeft}>
          <span style={styles.notifIcon}>⚠️</span>
          <div>
            <div style={styles.notifTitle}>
              You seem stuck on <strong>{n.problem_name}</strong> on {n.platform} ({n.failed_count} failed attempts)
            </div>
            <div style={styles.notifSub}>
              Paste your code in Suggestions tab to get instant help
            </div>
          </div>
        </div>
        <div style={styles.notifActions}>
          <button
            style={styles.notifHelpBtn}
            onClick={() => setActiveTab("suggestions")}
          >
            Get Help
          </button>
          <button
            style={styles.notifDismissBtn}
            onClick={async () => {
              await dismissNotification(n.id);
              setNotifications(prev => prev.filter(x => x.id !== n.id));
            }}
          >
            ✕
          </button>
        </div>
      </div>
    ))}
  </div>
)}
          {activeTab === "contests" && (
            <div style={styles.contentArea}>
              <div style={styles.cardHeader}>
                <h2 style={styles.cardTitle}>Upcoming Contests</h2>
                <span style={styles.contestCount}>{contests.length} contests</span>
              </div>
              {contests.length === 0 ? (
                <div style={styles.empty}>No upcoming contests found.</div>
              ) : (
                contests.map(contest => (
                  <ContestCard
                    key={contest.id}
                    contest={contest}
                    reminderSet={reminders[contest.id]}
                    calendarConnected={calendarConnected}
                    onReminder={() => handleReminder(contest.id)}
                    onCalendar={() => handleAddToCalendar(contest.id)}
                  />
                ))
              )}
            </div>
          )}

          {activeTab === "suggestions" && (
            <SuggestionsPanel suggestions={suggestions} />
          )}

          {activeTab === "progress" && (
            <div style={styles.contentArea}>
              <h2 style={styles.cardTitle}>Your Progress</h2>
              <div style={styles.statsGrid}>
                {[
                  { label: "Day Streak",       value: dashboard?.streak?.current || 0 },
                  { label: "Skill Rating",     value: dashboard?.profile?.skill_rating || 1200 },
                  { label: "Active Platforms", value: Object.values({ a: dashboard?.profile?.leetcode_handle, b: dashboard?.profile?.codeforces_handle, c: dashboard?.profile?.codechef_handle, d: dashboard?.profile?.atcoder_handle }).filter(Boolean).length },
                ].map(stat => (
                  <div key={stat.label} style={styles.statCard}>
                    <div style={styles.statNum}>{stat.value}</div>
                    <div style={styles.statLabel}>{stat.label}</div>
                  </div>
                ))}
              </div>
              {dashboard?.latest_suggestion && (
                <div style={styles.insightCard}>
                  <div style={styles.insightTitle}>Latest Concept Gap</div>
                  <div style={styles.insightConcept}>{dashboard.latest_suggestion.concept_gap}</div>
                  <div style={styles.insightNote}>{dashboard.latest_suggestion.tutoring_note}</div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  root: { minHeight: "100vh", background: "#0f0f1a", fontFamily: "sans-serif" },
  loading: { minHeight: "100vh", background: "#0f0f1a", display: "flex", alignItems: "center", justifyContent: "center" },
  loadingText: { color: "#7DF9C0", fontSize: "16px" },
  topbar: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 24px", background: "#1a1a2e", borderBottom: "0.5px solid #2a2a3e" },
  logo: { display: "flex", alignItems: "center", gap: "10px" },
  logoMark: { width: "32px", height: "32px", background: "#0f0f1a", borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", fontSize: "13px", fontWeight: "600", color: "#7DF9C0" },
  logoText: { fontSize: "17px", fontWeight: "700", color: "white", letterSpacing: "-0.5px" },
  nav: { display: "flex", gap: "4px" },
  navBtn: { padding: "6px 14px", borderRadius: "8px", fontSize: "13px", fontWeight: "500", border: "none", cursor: "pointer", background: "transparent", color: "#666" },
  navActive: { background: "#0f0f1a", color: "#7DF9C0" },
  topRight: { display: "flex", alignItems: "center", gap: "12px" },
  username: { color: "#666", fontSize: "13px" },
  logoutBtn: { padding: "6px 12px", background: "transparent", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "#666", cursor: "pointer", fontSize: "13px" },
  body: { display: "grid", gridTemplateColumns: "260px 1fr", height: "calc(100vh - 57px)", overflow: "hidden" },
  sidebar: { background: "#1a1a2e", borderRight: "0.5px solid #2a2a3e", padding: "20px 16px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "24px" },
  sideSection: { display: "flex", flexDirection: "column", gap: "8px" },
  sectionLabel: { fontSize: "10px", fontWeight: "500", letterSpacing: "1.5px", textTransform: "uppercase", color: "#444", marginBottom: "4px" },
  platformRow: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 10px", background: "#0f0f1a", borderRadius: "8px" },
  platformDot: { width: "8px", height: "8px", borderRadius: "50%" },
  platformName: { fontSize: "13px", fontWeight: "500", color: "white" },
  platformHandle: { 
  fontSize: "11px", 
  color: "#444", 
  fontFamily: "monospace",
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
  maxWidth: "100px"
},
  editBtn: { padding: "8px", background: "transparent", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "#666", cursor: "pointer", fontSize: "12px", marginTop: "4px" },
  calBtn: { padding: "10px", background: "transparent", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "#666", cursor: "pointer", fontSize: "13px", fontWeight: "500" },
  calConnected: { borderColor: "#7DF9C0", color: "#7DF9C0", cursor: "default" },
  calNote: { fontSize: "11px", color: "#444", lineHeight: "1.5" },
  main: { overflowY: "auto", padding: "20px" },
  contentArea: { display: "flex", flexDirection: "column", gap: "12px" },
  cardHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" },
  cardTitle: { fontSize: "16px", fontWeight: "600", color: "white", margin: 0 },
  contestCount: { fontSize: "12px", color: "#444", fontFamily: "monospace" },
  empty: { color: "#444", fontSize: "14px", padding: "24px", textAlign: "center" },
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "16px" },
  statCard: { background: "#1a1a2e", borderRadius: "12px", padding: "16px", border: "0.5px solid #2a2a3e" },
  statNum: { fontSize: "28px", fontWeight: "700", color: "#7DF9C0", fontFamily: "monospace", lineHeight: 1 },
  statLabel: { fontSize: "11px", color: "#444", marginTop: "4px" },
  insightCard: { background: "#1a1a2e", borderRadius: "12px", padding: "16px", border: "0.5px solid #2a2a3e" },
  insightTitle: { fontSize: "11px", fontWeight: "500", letterSpacing: "1px", textTransform: "uppercase", color: "#444", marginBottom: "8px" },
  insightConcept: { fontSize: "14px", fontWeight: "600", color: "#7DF9C0", marginBottom: "8px" },
  insightNote: { fontSize: "13px", color: "#888", lineHeight: "1.5" },
  notifBanner:     { display: "flex", flexDirection: "column", gap: "8px", marginBottom: "8px" },
notifItem:       { display: "flex", alignItems: "center", justifyContent: "space-between", background: "#1a0f0f", border: "0.5px solid #ef4444", borderRadius: "10px", padding: "12px 16px", gap: "12px" },
notifLeft:       { display: "flex", alignItems: "flex-start", gap: "10px", flex: 1 },
notifIcon:       { fontSize: "18px", flexShrink: 0 },
notifTitle:      { fontSize: "13px", color: "white", lineHeight: "1.4", marginBottom: "2px" },
notifSub:        { fontSize: "11px", color: "#888" },
notifActions:    { display: "flex", gap: "6px", flexShrink: 0 },
notifHelpBtn:    { padding: "6px 12px", background: "#7DF9C0", border: "none", borderRadius: "6px", color: "#0f0f1a", fontSize: "12px", fontWeight: "700", cursor: "pointer" },
notifDismissBtn: { padding: "6px 10px", background: "transparent", border: "0.5px solid #444", borderRadius: "6px", color: "#666", fontSize: "12px", cursor: "pointer" },
};
