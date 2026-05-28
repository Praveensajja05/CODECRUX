import React, { useState, useEffect } from "react";

const PLATFORM_COLORS = {
  leetcode:   { bg: "#fff3e0", color: "#e65100", label: "LeetCode" },
  codeforces: { bg: "#e3f2fd", color: "#1565c0", label: "Codeforces" },
  codechef:   { bg: "#f3e5f5", color: "#6a1b9a", label: "CodeChef" },
  atcoder:    { bg: "#e8f5e9", color: "#2e7d32", label: "AtCoder" },
};

function getTimeLeft(isoString) {
  const diff = new Date(isoString) - new Date();
  if (diff <= 0) return null;

  const days    = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours   = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  return { days, hours, minutes, seconds, diff };
}

function formatStartDate(isoString) {
  return new Date(isoString).toLocaleDateString("en-IN", {
    day: "numeric", month: "short",
    hour: "2-digit", minute: "2-digit", hour12: true
  });
}

function CountdownTimer({ startTime }) {
  const [timeLeft, setTimeLeft] = useState(getTimeLeft(startTime));

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeLeft(getTimeLeft(startTime));
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);

  if (!timeLeft) {
    return <span style={styles.liveTimer}>● Live now</span>;
  }

  const { days, hours, minutes, seconds, diff } = timeLeft;
  const isUrgent = diff < 60 * 60 * 1000; // less than 1 hour

  if (days > 0) {
    return (
      <span style={styles.timerNormal}>
        {days}d {hours}h {minutes}m
      </span>
    );
  }

  return (
    <div style={styles.timerRow}>
      {hours > 0 && (
        <div style={{ ...styles.timerBlock, ...(isUrgent ? styles.timerUrgent : {}) }}>
          <span style={styles.timerNum}>{String(hours).padStart(2, "0")}</span>
          <span style={styles.timerUnit}>hr</span>
        </div>
      )}
      <div style={{ ...styles.timerBlock, ...(isUrgent ? styles.timerUrgent : {}) }}>
        <span style={styles.timerNum}>{String(minutes).padStart(2, "0")}</span>
        <span style={styles.timerUnit}>min</span>
      </div>
      <div style={{ ...styles.timerBlock, ...(isUrgent ? styles.timerUrgent : {}) }}>
        <span style={styles.timerNum}>{String(seconds).padStart(2, "0")}</span>
        <span style={styles.timerUnit}>sec</span>
      </div>
    </div>
  );
}

export default function ContestCard({ contest, reminderSet, calendarConnected, onReminder, onCalendar }) {
  const platform = PLATFORM_COLORS[contest.platform] || { bg: "#f5f5f5", color: "#333", label: contest.platform };
  const isLive   = new Date(contest.start_time) <= new Date();

  return (
    <div style={styles.card}>
      <div style={styles.row}>
        {/* Left */}
        <div style={styles.left}>
          <div style={styles.tagRow}>
            <span style={{ ...styles.platformTag, background: platform.bg, color: platform.color }}>
              {platform.label}
            </span>
            {isLive && <span style={styles.liveBadge}>● LIVE</span>}
          </div>
          <div style={styles.title}>{contest.title}</div>
          <div style={styles.meta}>
            <span>{formatStartDate(contest.start_time)}</span>
            {contest.duration_mins && <span style={styles.separator}>·</span>}
            {contest.duration_mins && <span>{contest.duration_mins} min</span>}
          </div>
        </div>

        {/* Right */}
        <div style={styles.right}>
          <div style={styles.actions}>
            {calendarConnected && (
              <button style={styles.iconBtn} onClick={onCalendar} title="Add to Google Calendar">📅</button>
            )}
            <button
              style={{ ...styles.iconBtn, ...(reminderSet ? styles.iconBtnActive : {}) }}
              onClick={onReminder}
              title={reminderSet ? "Remove reminder" : "Set 30 min reminder"}
            >
              🔔
            </button>
          </div>
          <CountdownTimer startTime={contest.start_time} />
          <a href={contest.url} target="_blank" rel="noreferrer" style={styles.openLink}>Open →</a>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: { background: "#1a1a2e", borderRadius: "10px", padding: "14px 16px", border: "0.5px solid #2a2a3e", marginBottom: "8px" },
  row:  { display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px" },
  left: { display: "flex", flexDirection: "column", gap: "5px", flex: 1, minWidth: 0 },
  tagRow: { display: "flex", alignItems: "center", gap: "8px" },
  platformTag: { fontSize: "10px", fontWeight: "700", padding: "2px 8px", borderRadius: "4px", letterSpacing: "0.3px" },
  liveBadge: { fontSize: "10px", fontWeight: "600", color: "#22c55e", letterSpacing: "0.5px" },
  title: { fontSize: "14px", fontWeight: "500", color: "white", lineHeight: "1.3", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" },
  meta: { display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#555", fontFamily: "monospace" },
  separator: { color: "#333" },
  right: { display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "6px", flexShrink: 0 },
  actions: { display: "flex", gap: "6px" },
  iconBtn: { width: "30px", height: "30px", borderRadius: "6px", border: "0.5px solid #2a2a3e", background: "#0f0f1a", cursor: "pointer", fontSize: "14px", display: "flex", alignItems: "center", justifyContent: "center" },
  iconBtnActive: { background: "#0d2818", borderColor: "#7DF9C0" },
  openLink: { color: "#7DF9C0", textDecoration: "none", fontSize: "11px", fontWeight: "500", fontFamily: "monospace" },

  // Timer styles
  timerRow: { display: "flex", gap: "4px", alignItems: "center" },
  timerBlock: { display: "flex", flexDirection: "column", alignItems: "center", background: "#0f0f1a", borderRadius: "6px", padding: "4px 8px", border: "0.5px solid #2a2a3e", minWidth: "36px" },
  timerUrgent: { border: "0.5px solid #ef4444", background: "#1a0808" },
  timerNum: { fontSize: "14px", fontWeight: "700", color: "#7DF9C0", fontFamily: "monospace", lineHeight: 1 },
  timerUnit: { fontSize: "9px", color: "#444", marginTop: "2px", letterSpacing: "0.5px" },
  timerNormal: { fontSize: "12px", color: "#7DF9C0", fontFamily: "monospace", fontWeight: "600" },
  liveTimer: { fontSize: "12px", color: "#22c55e", fontWeight: "600", fontFamily: "monospace" },
};
