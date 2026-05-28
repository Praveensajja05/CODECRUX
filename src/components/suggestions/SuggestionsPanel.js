import React, { useState } from "react";
import { analyzecode } from "../../utils/api";
import toast from "react-hot-toast";

const DIFFICULTY_COLORS = {
  easy: { bg: "#ecfdf5", color: "#14532d" },
  med:  { bg: "#fffbeb", color: "#92400e" },
  hard: { bg: "#fef2f2", color: "#991b1b" },
};

function difficultyLabel(rating) {
  if (!rating) return null;
  if (rating < 1200) return "easy";
  if (rating < 1600) return "med";
  return "hard";
}

export default function SuggestionsPanel({ suggestions, onNewSuggestions }) {
  const [showForm, setShowForm]       = useState(false);
  const [analyzing, setAnalyzing]     = useState(false);
  const [result, setResult]           = useState(suggestions);
  const [form, setForm] = useState({
    problem_title:   "",
    problem_url:     "",
    problem_tags:    "",
    difficulty:      "Medium",
    code:            "",
    language:        "python",
    verdict:         "Wrong Answer",
    time_spent:      "20",
    prior_attempts:  "2",
  });

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!form.code.trim()) {
      toast.error("Please paste your code");
      return;
    }
    if (!form.problem_title.trim()) {
      toast.error("Please enter the problem name");
      return;
    }

    setAnalyzing(true);
    try {
      const res = await analyzecode({
        problem: {
          id: form.problem_url || form.problem_title.toLowerCase().replace(/\s+/g, "-"),
          title: form.problem_title,
          statement: "",
          tags: form.problem_tags.split(",").map(t => t.trim()).filter(Boolean),
          difficulty: form.difficulty,
          correct_approach_hint: ""
        },
        submission: {
          code: form.code,
          language: form.language,
          verdict: form.verdict,
          time_spent_minutes: parseInt(form.time_spent) || 20,
          prior_attempts: parseInt(form.prior_attempts) || 1
        }
      });

      setResult(res.data);
      setShowForm(false);
      toast.success("Analysis complete!");
      if (onNewSuggestions) onNewSuggestions(res.data);
    } catch (err) {
      toast.error(err.response?.data?.error || "Analysis failed. Try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div style={styles.container}>

      {/* Get Help Button */}
      <div style={styles.topRow}>
        <div>
          <h2 style={styles.pageTitle}>CodeCrux Suggestions</h2>
          <p style={styles.pageSubtitle}>
            Paste your code to get instant diagnosis and targeted practice problems.
          </p>
        </div>
        <button
          style={styles.getHelpBtn}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? "✕ Cancel" : "⚡ Get Help"}
        </button>
      </div>

      {/* Get Help Form */}
      {showForm && (
        <div style={styles.formCard}>
          <div style={styles.formTitle}>Tell CodeCrux what you're stuck on</div>
          <form onSubmit={handleAnalyze} style={styles.form}>

            <div style={styles.formRow}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Problem name *</label>
                <input
                  style={styles.input}
                  name="problem_title"
                  placeholder="e.g. Binary Tree Maximum Path Sum"
                  value={form.problem_title}
                  onChange={handleChange}
                  required
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Problem URL (optional)</label>
                <input
                  style={styles.input}
                  name="problem_url"
                  placeholder="https://leetcode.com/problems/..."
                  value={form.problem_url}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div style={styles.formRow}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Tags (comma separated)</label>
                <input
                  style={styles.input}
                  name="problem_tags"
                  placeholder="e.g. tree, dfs, dp"
                  value={form.problem_tags}
                  onChange={handleChange}
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Difficulty</label>
                <select style={styles.select} name="difficulty" value={form.difficulty} onChange={handleChange}>
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
              </div>
            </div>

            <div style={styles.formRow}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Language</label>
                <select style={styles.select} name="language" value={form.language} onChange={handleChange}>
                  <option value="python">Python</option>
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Verdict</label>
                <select style={styles.select} name="verdict" value={form.verdict} onChange={handleChange}>
                  <option>Wrong Answer</option>
                  <option>Time Limit Exceeded</option>
                  <option>Runtime Error</option>
                  <option>Memory Limit Exceeded</option>
                  <option>Compilation Error</option>
                </select>
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Time spent (min)</label>
                <input
                  style={styles.input}
                  name="time_spent"
                  type="number"
                  min="1"
                  value={form.time_spent}
                  onChange={handleChange}
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Attempts</label>
                <input
                  style={styles.input}
                  name="prior_attempts"
                  type="number"
                  min="1"
                  value={form.prior_attempts}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Your code *</label>
              <textarea
                style={styles.textarea}
                name="code"
                placeholder="Paste your code here..."
                value={form.code}
                onChange={handleChange}
                rows={10}
                required
              />
            </div>

            <button style={styles.analyzeBtn} type="submit" disabled={analyzing}>
              {analyzing ? "Analyzing your code..." : "⚡ Analyze My Code"}
            </button>
          </form>
        </div>
      )}

      {/* Results */}
      {!showForm && result && (
        <div style={styles.resultsContainer}>
          {/* Header */}
          <div style={styles.header}>
            <div style={styles.headerLeft}>
              <span style={styles.pulse} />
              <span style={styles.headerTitle}>Analysis Results</span>
            </div>
            <span style={styles.mlChip}>ML monitoring active</span>
          </div>

          {/* Concept Gap */}
          {result.concept_gap || result.diagnosis?.specific_concept_missing ? (
            <div style={styles.gapCard}>
              <div style={styles.gapLabel}>Identified concept gap</div>
              <div style={styles.gapConcept}>
                {result.concept_gap || result.diagnosis?.specific_concept_missing}
              </div>
              {(result.tutoring_note || result.diagnosis?.tutoring_note) && (
                <div style={styles.tutoringNote}>
                  {result.tutoring_note || result.diagnosis?.tutoring_note}
                </div>
              )}
              {result.diagnosis?.gap_type && (
                <div style={styles.gapType}>
                  Gap type: <strong>{result.diagnosis.gap_type.replace(/_/g, " ")}</strong>
                  {" · "}Confidence: <strong>{Math.round((result.diagnosis.confidence || 0) * 100)}%</strong>
                </div>
              )}
            </div>
          ) : null}

          {/* Suggestions */}
          {result.suggestions && result.suggestions.length > 0 ? (
            <div style={styles.list}>
              <div style={styles.listTitle}>Recommended practice problems</div>
              {result.suggestions.map((s, i) => {
                const diff      = difficultyLabel(s.difficulty);
                const diffStyle = diff ? DIFFICULTY_COLORS[diff] : null;
                return (
                  <a
                    key={i}
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    style={styles.item}
                  >
                    <div style={styles.itemLeft}>
                      <div style={styles.itemRank}>{i + 1}</div>
                      <div style={styles.itemContent}>
                        <div style={styles.itemHeader}>
                          <span style={styles.itemTitle}>{s.title}</span>
                          {diffStyle && (
                            <span style={{ ...styles.diffBadge, background: diffStyle.bg, color: diffStyle.color }}>
                              {diff}
                            </span>
                          )}
                        </div>
                        <div style={styles.itemWhy}>{s.why}</div>
                        <div style={styles.itemTags}>
                          <span style={styles.platformTag}>{s.platform}</span>
                          {(s.key_concepts || []).slice(0, 2).map((c, j) => (
                            <span key={j} style={styles.conceptTag}>{c}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div style={styles.similarity}>
                      {Math.round((s.similarity_score || 0) * 100)}% match
                    </div>
                  </a>
                );
              })}
            </div>
          ) : null}

          <button
            style={styles.tryAnotherBtn}
            onClick={() => { setShowForm(true); setResult(null); }}
          >
            ⚡ Analyze another problem
          </button>
        </div>
      )}

      {/* Empty state */}
      {!showForm && !result && (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>🤖</div>
          <div style={styles.emptyTitle}>No analysis yet</div>
          <div style={styles.emptyText}>
            Click "Get Help" above, paste your code, and CodeCrux will identify exactly what you're missing and suggest targeted practice problems.
          </div>
          <button style={styles.getHelpBtnEmpty} onClick={() => setShowForm(true)}>
            ⚡ Get Help Now
          </button>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", gap: "16px" },
  topRow: { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  pageTitle: { fontSize: "18px", fontWeight: "700", color: "white", margin: "0 0 4px" },
  pageSubtitle: { fontSize: "13px", color: "#555", margin: 0 },
  getHelpBtn: { padding: "10px 20px", background: "#7DF9C0", border: "none", borderRadius: "8px", color: "#0f0f1a", fontSize: "13px", fontWeight: "700", cursor: "pointer", flexShrink: 0 },

  formCard: { background: "#1a1a2e", borderRadius: "12px", padding: "20px", border: "0.5px solid #2a2a3e" },
  formTitle: { fontSize: "14px", fontWeight: "600", color: "white", marginBottom: "16px" },
  form: { display: "flex", flexDirection: "column", gap: "12px" },
  formRow: { display: "flex", gap: "12px" },
  formGroup: { display: "flex", flexDirection: "column", gap: "5px", flex: 1 },
  label: { fontSize: "11px", fontWeight: "500", color: "#555", letterSpacing: "0.5px", textTransform: "uppercase" },
  input: { padding: "9px 12px", background: "#0f0f1a", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "white", fontSize: "13px", outline: "none", fontFamily: "monospace" },
  select: { padding: "9px 12px", background: "#0f0f1a", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "white", fontSize: "13px", outline: "none" },
  textarea: { padding: "12px", background: "#0f0f1a", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "#7DF9C0", fontSize: "12px", outline: "none", fontFamily: "monospace", resize: "vertical", lineHeight: "1.5" },
  analyzeBtn: { padding: "12px", background: "#7DF9C0", border: "none", borderRadius: "8px", color: "#0f0f1a", fontSize: "14px", fontWeight: "700", cursor: "pointer" },

  resultsContainer: { display: "flex", flexDirection: "column", gap: "12px" },
  header: { background: "#1a1a2e", borderRadius: "12px 12px 0 0", padding: "14px 18px", display: "flex", alignItems: "center", justifyContent: "space-between", border: "0.5px solid #2a2a3e" },
  headerLeft: { display: "flex", alignItems: "center", gap: "8px" },
  pulse: { width: "8px", height: "8px", borderRadius: "50%", background: "#7DF9C0", display: "inline-block" },
  headerTitle: { fontSize: "14px", fontWeight: "600", color: "#7DF9C0" },
  mlChip: { fontSize: "10px", fontWeight: "500", padding: "2px 8px", borderRadius: "20px", background: "rgba(125,249,192,0.1)", color: "#7DF9C0", fontFamily: "monospace" },

  gapCard: { background: "#1a1a2e", padding: "16px 18px", border: "0.5px solid #2a2a3e", borderTop: "none" },
  gapLabel: { fontSize: "10px", fontWeight: "500", letterSpacing: "1px", textTransform: "uppercase", color: "#444", marginBottom: "6px" },
  gapConcept: { fontSize: "15px", fontWeight: "700", color: "#7DF9C0", marginBottom: "10px" },
  tutoringNote: { fontSize: "13px", color: "#888", lineHeight: "1.6", padding: "12px", background: "#0f0f1a", borderRadius: "8px", borderLeft: "3px solid #7DF9C0", marginBottom: "8px" },
  gapType: { fontSize: "11px", color: "#444", fontFamily: "monospace" },

  listTitle: { fontSize: "12px", fontWeight: "600", color: "#555", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "4px" },
  list: { display: "flex", flexDirection: "column", gap: "8px" },
  item: { display: "flex", alignItems: "center", justifyContent: "space-between", background: "#1a1a2e", borderRadius: "12px", padding: "14px 16px", border: "0.5px solid #2a2a3e", textDecoration: "none" },
  itemLeft: { display: "flex", alignItems: "flex-start", gap: "12px", flex: 1 },
  itemRank: { width: "24px", height: "24px", borderRadius: "50%", background: "#0f0f1a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "11px", fontWeight: "600", color: "#7DF9C0", flexShrink: 0 },
  itemContent: { flex: 1 },
  itemHeader: { display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" },
  itemTitle: { fontSize: "13px", fontWeight: "500", color: "white" },
  diffBadge: { fontSize: "10px", fontWeight: "500", padding: "1px 6px", borderRadius: "4px" },
  itemWhy: { fontSize: "12px", color: "#666", lineHeight: "1.4", marginBottom: "6px" },
  itemTags: { display: "flex", gap: "5px", flexWrap: "wrap" },
  platformTag: { fontSize: "10px", fontWeight: "500", padding: "1px 6px", borderRadius: "4px", background: "#0f0f1a", color: "#444", border: "0.5px solid #2a2a3e" },
  conceptTag: { fontSize: "10px", padding: "1px 6px", borderRadius: "4px", background: "#0f0f1a", color: "#444", border: "0.5px solid #2a2a3e", fontFamily: "monospace" },
  similarity: { fontSize: "11px", color: "#444", fontFamily: "monospace", flexShrink: 0 },

  tryAnotherBtn: { padding: "10px 20px", background: "transparent", border: "0.5px solid #2a2a3e", borderRadius: "8px", color: "#7DF9C0", fontSize: "13px", fontWeight: "600", cursor: "pointer", alignSelf: "flex-start" },

  empty: { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "60px 20px", textAlign: "center" },
  emptyIcon: { fontSize: "48px", marginBottom: "16px" },
  emptyTitle: { fontSize: "16px", fontWeight: "600", color: "white", marginBottom: "8px" },
  emptyText: { fontSize: "13px", color: "#444", maxWidth: "400px", lineHeight: "1.6", marginBottom: "20px" },
  getHelpBtnEmpty: { padding: "12px 24px", background: "#7DF9C0", border: "none", borderRadius: "8px", color: "#0f0f1a", fontSize: "14px", fontWeight: "700", cursor: "pointer" },
};
