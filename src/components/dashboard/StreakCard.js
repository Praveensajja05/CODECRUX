import React from "react";

export default function StreakCard({ streak }) {
  const current = streak?.current || 0;
  const dates   = streak?.dates || [];

  return (
    <div style={styles.card}>
      <div style={styles.num}>{current}</div>
      <div style={styles.label}>day streak</div>
      <div style={styles.dots}>
        {Array.from({ length: 14 }).map((_, i) => {
          const isActive = i < dates.length;
          const isToday  = i === 0;
          return (
            <div
              key={i}
              style={{
                ...styles.dot,
                background: isActive ? "#7DF9C0" : "#1a1a2e",
                outline: isToday && isActive ? "2px solid rgba(125,249,192,0.4)" : "none",
              }}
            />
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  card: { background: "#0f0f1a", borderRadius: "12px", padding: "16px", border: "0.5px solid #2a2a3e" },
  num:  { fontSize: "42px", fontWeight: "700", fontFamily: "monospace", color: "#7DF9C0", lineHeight: 1 },
  label: { fontSize: "12px", color: "#444", marginTop: "4px", marginBottom: "14px" },
  dots: { display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "4px" },
  dot:  { width: "100%", aspectRatio: "1", borderRadius: "3px" },
};
