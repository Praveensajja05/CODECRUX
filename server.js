/**
 * CodeCrux Backend - Complete Single File
 * ----------------------------------------
 * Run: node server.js
 *
 * Requires .env file with:
 *   PORT=3001
 *   DATABASE_URL=postgresql://postgres:postgres123@127.0.0.1:5432/codecrux
 *   REDIS_URL=redis://127.0.0.1:6379
 *   JWT_SECRET=codecrux_secret_change_this
 *   ML_SERVICE_URL=http://localhost:8001
 *   EMAIL_USER=your_gmail@gmail.com
 *   EMAIL_PASS=your_gmail_app_password
 */

const express      = require("express");
const cors         = require("cors");
const dotenv       = require("dotenv");
const axios        = require("axios");
const { Pool }     = require("pg");
const redis        = require("redis");
const jwt          = require("jsonwebtoken");
const bcrypt       = require("bcryptjs");
const cron         = require("node-cron");
const nodemailer   = require("nodemailer");
const { calendarRoutes } = require("./calendar");
const { startPoller , pollerRoutes } = require ( "./poller");

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────

const PORT          = process.env.PORT || 3001;
const JWT_SECRET    = process.env.JWT_SECRET || "codecrux_secret";
const ML_URL        = process.env.ML_SERVICE_URL || "http://localhost:8001";
const DATABASE_URL  = process.env.DATABASE_URL || "postgresql://postgres:postgres123@127.0.0.1:5432/codecrux";
const REDIS_URL     = process.env.REDIS_URL || "redis://127.0.0.1:6379";

// ─────────────────────────────────────────────
// DATABASE
// ─────────────────────────────────────────────

const pool = new Pool({ connectionString: DATABASE_URL });

async function query(text, params) {
  const client = await pool.connect();
  try {
    const res = await client.query(text, params);
    return res;
  } finally {
    client.release();
  }
}

async function setupDatabase() {
  console.log("Setting up backend database tables...");

  await query(`
    CREATE TABLE IF NOT EXISTS students (
      id            BIGSERIAL PRIMARY KEY,
      email         TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      username      TEXT UNIQUE NOT NULL,
      created_at    TIMESTAMPTZ DEFAULT NOW()
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS student_profiles (
      student_id        BIGINT PRIMARY KEY REFERENCES students(id),
      leetcode_handle   TEXT,
      codeforces_handle TEXT,
      codechef_handle   TEXT,
      atcoder_handle    TEXT,
      skill_rating      INTEGER DEFAULT 1200,
      updated_at        TIMESTAMPTZ DEFAULT NOW()
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS contests (
      id            TEXT PRIMARY KEY,
      platform      TEXT NOT NULL,
      title         TEXT NOT NULL,
      start_time    TIMESTAMPTZ NOT NULL,
      duration_mins INTEGER,
      url           TEXT,
      fetched_at    TIMESTAMPTZ DEFAULT NOW()
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS contest_reminders (
      id          BIGSERIAL PRIMARY KEY,
      student_id  BIGINT REFERENCES students(id),
      contest_id  TEXT REFERENCES contests(id),
      notified    BOOLEAN DEFAULT FALSE,
      created_at  TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(student_id, contest_id)
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS daily_activity (
      id          BIGSERIAL PRIMARY KEY,
      student_id  BIGINT REFERENCES students(id),
      activity_date DATE NOT NULL,
      problems_solved INTEGER DEFAULT 0,
      platforms   TEXT[],
      created_at  TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(student_id, activity_date)
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS struggle_events (
      id            BIGSERIAL PRIMARY KEY,
      student_id    BIGINT REFERENCES students(id),
      problem_id    TEXT,
      problem_title TEXT,
      failed_attempts INTEGER DEFAULT 0,
      time_spent_min  INTEGER DEFAULT 0,
      last_code     TEXT,
      language      TEXT,
      verdict       TEXT,
      ml_analyzed   BOOLEAN DEFAULT FALSE,
      created_at    TIMESTAMPTZ DEFAULT NOW()
    );
  `);

  await query(`
    CREATE TABLE IF NOT EXISTS ml_suggestions (
      id            BIGSERIAL PRIMARY KEY,
      student_id    BIGINT REFERENCES students(id),
      concept_gap   TEXT,
      tutoring_note TEXT,
      suggestions   JSONB,
      seen          BOOLEAN DEFAULT FALSE,
      created_at    TIMESTAMPTZ DEFAULT NOW()
    );
  `);

  console.log("Backend database tables ready.");
}

// ─────────────────────────────────────────────
// REDIS
// ─────────────────────────────────────────────

const redisClient = redis.createClient({ 
  url: REDIS_URL,
  socket: {
    tls: true,
    rejectUnauthorized: false
  }
});
redisClient.on("error", (err) => console.log("Redis error:", err));

async function cacheGet(key) {
  try {
    const val = await redisClient.get(key);
    return val ? JSON.parse(val) : null;
  } catch { return null; }
}

async function cacheSet(key, value, ttlSeconds = 300) {
  try {
    await redisClient.setEx(key, ttlSeconds, JSON.stringify(value));
  } catch {}
}

// ─────────────────────────────────────────────
// EMAIL
// ─────────────────────────────────────────────

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

async function sendEmail(to, subject, html) {
  if (!process.env.EMAIL_USER) {
    console.log(`[Email skipped - no EMAIL_USER set] To: ${to} Subject: ${subject}`);
    return;
  }
  try {
    await transporter.sendMail({ from: process.env.EMAIL_USER, to, subject, html });
    console.log(`Email sent to ${to}`);
  } catch (err) {
    console.log(`Email failed: ${err.message}`);
  }
}

// ─────────────────────────────────────────────
// AUTH MIDDLEWARE
// ─────────────────────────────────────────────

function authMiddleware(req, res, next) {
  const header = req.headers.authorization;
  if (!header || !header.startsWith("Bearer ")) {
    return res.status(401).json({ error: "No token provided" });
  }
  const token = header.split(" ")[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.studentId = decoded.id;
    req.email = decoded.email;
    next();
  } catch {
    return res.status(401).json({ error: "Invalid token" });
  }
}

// ─────────────────────────────────────────────
// CONTEST FETCHERS
// ─────────────────────────────────────────────

async function fetchCodeforcesContests() {
  try {
    const res = await axios.get("https://codeforces.com/api/contest.list", {
      timeout: 10000
    });
    if (res.data.status !== "OK") return [];

    const upcoming = res.data.result
      .filter(c => c.phase === "BEFORE")
      .slice(0, 10)
      .map(c => ({
        id: `cf-${c.id}`,
        platform: "codeforces",
        title: c.name,
        start_time: new Date(c.startTimeSeconds * 1000).toISOString(),
        duration_mins: Math.floor(c.durationSeconds / 60),
        url: `https://codeforces.com/contest/${c.id}`
      }));

    console.log(`Fetched ${upcoming.length} Codeforces contests`);
    return upcoming;
  } catch (err) {
    console.log(`Codeforces fetch failed: ${err.message}`);
    return [];
  }
}

async function fetchLeetcodeContests() {
  try {
    const res = await axios.post(
      "https://leetcode.com/graphql",
      {
        query: `{
          allContests {
            title
            titleSlug
            startTime
            duration
          }
        }`
      },
      {
        headers: { "Content-Type": "application/json" },
        timeout: 10000
      }
    );

    const now = Date.now() / 1000;
    const upcoming = (res.data?.data?.allContests || [])
      .filter(c => c.startTime > now)
      .slice(0, 5)
      .map(c => ({
        id: `lc-${c.titleSlug}`,
        platform: "leetcode",
        title: c.title,
        start_time: new Date(c.startTime * 1000).toISOString(),
        duration_mins: Math.floor(c.duration / 60),
        url: `https://leetcode.com/contest/${c.titleSlug}`
      }));

    console.log(`Fetched ${upcoming.length} LeetCode contests`);
    return upcoming;
  } catch (err) {
    console.log(`LeetCode fetch failed: ${err.message}`);
    return [];
  }
}

async function fetchAndStoreContests() {
  console.log("Fetching contests from all platforms...");
  const [cf, lc] = await Promise.all([
    fetchCodeforcesContests(),
    fetchLeetcodeContests()
  ]);

  const all = [...cf, ...lc];

  for (const contest of all) {
    try {
      await query(`
        INSERT INTO contests (id, platform, title, start_time, duration_mins, url)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
          title = EXCLUDED.title,
          start_time = EXCLUDED.start_time,
          fetched_at = NOW()
      `, [contest.id, contest.platform, contest.title,
          contest.start_time, contest.duration_mins, contest.url]);
    } catch (err) {
      console.log(`Failed to store contest ${contest.id}: ${err.message}`);
    }
  }

  await cacheSet("contests:all", all, 1800);
  console.log(`Stored ${all.length} contests total`);
  return all;
}

// ─────────────────────────────────────────────
// STREAK HELPERS
// ─────────────────────────────────────────────

async function logActivity(studentId, platform) {
  const today = new Date().toISOString().split("T")[0];
  await query(`
    INSERT INTO daily_activity (student_id, activity_date, problems_solved, platforms)
    VALUES ($1, $2, 1, ARRAY[$3])
    ON CONFLICT (student_id, activity_date) DO UPDATE SET
      problems_solved = daily_activity.problems_solved + 1,
      platforms = array_append(
        array_remove(daily_activity.platforms, $3), $3
      )
  `, [studentId, today, platform]);
}

async function getStreak(studentId) {
  const res = await query(`
    SELECT activity_date
    FROM daily_activity
    WHERE student_id = $1
    ORDER BY activity_date DESC
    LIMIT 30
  `, [studentId]);

  if (res.rows.length === 0) return { current: 0, longest: 0, dates: [] };

  const dates = res.rows.map(r =>
    new Date(r.activity_date).toISOString().split("T")[0]
  );

  let current = 0;
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];

  if (dates[0] === today || dates[0] === yesterday) {
    current = 1;
    for (let i = 1; i < dates.length; i++) {
      const prev = new Date(new Date(dates[i-1]) - 86400000).toISOString().split("T")[0];
      if (dates[i] === prev) current++;
      else break;
    }
  }

  return { current, dates: dates.slice(0, 14) };
}

// ─────────────────────────────────────────────
// ML SERVICE BRIDGE
// ─────────────────────────────────────────────

async function callMLAnalyze(studentId, problem, submission) {
  try {
    const res = await axios.post(`${ML_URL}/analyze`, {
      user_id: String(studentId),
      problem,
      submission,
      user_context: { user_id: String(studentId) }
    }, { timeout: 30000 });
    return res.data;
  } catch (err) {
    console.log(`ML analyze failed: ${err.message}`);
    return null;
  }
}

async function checkAndTriggerAnalysis(studentId, problemId, problemTitle, code, language, verdict, timeSpent) {
  // Get or create struggle event
  const existing = await query(`
    SELECT * FROM struggle_events
    WHERE student_id = $1 AND problem_id = $2
    ORDER BY created_at DESC LIMIT 1
  `, [studentId, problemId]);

  let attempts = 1;
  let totalTime = timeSpent;

  if (existing.rows.length > 0) {
    attempts = existing.rows[0].failed_attempts + 1;
    totalTime = existing.rows[0].time_spent_min + timeSpent;

    await query(`
      UPDATE struggle_events
      SET failed_attempts = $1, time_spent_min = $2,
          last_code = $3, verdict = $4
      WHERE id = $5
    `, [attempts, totalTime, code, verdict, existing.rows[0].id]);
  } else {
    await query(`
      INSERT INTO struggle_events
        (student_id, problem_id, problem_title, failed_attempts, time_spent_min, last_code, language, verdict)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `, [studentId, problemId, problemTitle, attempts, totalTime, code, language, verdict]);
  }

  // Trigger ML if student is struggling (2+ failures or 20+ minutes)
  const shouldAnalyze = attempts >= 2 || totalTime >= 20;

  if (shouldAnalyze && verdict !== "AC") {
    console.log(`Triggering ML analysis for student ${studentId} on problem ${problemTitle}`);

    const mlResult = await callMLAnalyze(studentId, {
      id: problemId,
      title: problemTitle,
      statement: "",
      tags: [],
      difficulty: "unknown"
    }, {
      code,
      language,
      verdict,
      time_spent_minutes: totalTime,
      prior_attempts: attempts
    });

    if (mlResult && mlResult.diagnosis) {
      await query(`
        INSERT INTO ml_suggestions
          (student_id, concept_gap, tutoring_note, suggestions)
        VALUES ($1, $2, $3, $4)
      `, [
        studentId,
        mlResult.diagnosis.specific_concept_missing,
        mlResult.diagnosis.tutoring_note,
        JSON.stringify(mlResult.suggestions || [])
      ]);

      console.log(`ML suggestions saved for student ${studentId}`);
    }
  }
}

// ─────────────────────────────────────────────
// NOTIFICATION CRON
// ─────────────────────────────────────────────

async function checkContestReminders() {
  const now = new Date();
  const in35Mins = new Date(now.getTime() + 35 * 60 * 1000);
  const in25Mins = new Date(now.getTime() + 25 * 60 * 1000);

  const res = await query(`
    SELECT cr.id, cr.student_id, cr.contest_id,
           s.email, s.username,
           c.title, c.platform, c.start_time, c.url
    FROM contest_reminders cr
    JOIN students s ON cr.student_id = s.id
    JOIN contests c ON cr.contest_id = c.id
    WHERE cr.notified = FALSE
      AND c.start_time BETWEEN $1 AND $2
  `, [in25Mins.toISOString(), in35Mins.toISOString()]);

  for (const row of res.rows) {
    const minsLeft = Math.round((new Date(row.start_time) - now) / 60000);

    await sendEmail(
      row.email,
      `⏰ Contest starting in ${minsLeft} minutes: ${row.title}`,
      `
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #1a1a2e;">CodeCrux Contest Reminder</h2>
          <p>Hi <strong>${row.username}</strong>,</p>
          <p>Your contest is starting soon!</p>
          <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <h3 style="margin: 0 0 8px;">${row.title}</h3>
            <p style="margin: 4px 0;">Platform: <strong>${row.platform}</strong></p>
            <p style="margin: 4px 0;">Starts in: <strong>${minsLeft} minutes</strong></p>
          </div>
          <a href="${row.url}" style="background: #1a1a2e; color: #7DF9C0; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block;">
            Join Contest
          </a>
          <p style="color: #999; font-size: 12px; margin-top: 24px;">CodeCrux - Your coding tutor</p>
        </div>
      `
    );

    await query(`
      UPDATE contest_reminders SET notified = TRUE WHERE id = $1
    `, [row.id]);
  }
}

// ─────────────────────────────────────────────
// ROUTES - AUTH
// ─────────────────────────────────────────────

app.post("/api/auth/register", async (req, res) => {
  const { email, password, username } = req.body;
  if (!email || !password || !username) {
    return res.status(400).json({ error: "email, password, username required" });
  }
  try {
    const hash = await bcrypt.hash(password, 10);
    const result = await query(`
      INSERT INTO students (email, password_hash, username)
      VALUES ($1, $2, $3) RETURNING id, email, username
    `, [email, hash, username]);

    const student = result.rows[0];

    await query(`
      INSERT INTO student_profiles (student_id) VALUES ($1)
    `, [student.id]);

    const token = jwt.sign({ id: student.id, email: student.email }, JWT_SECRET, { expiresIn: "30d" });

    res.json({ token, student: { id: student.id, email: student.email, username: student.username } });
  } catch (err) {
    if (err.code === "23505") {
      return res.status(400).json({ error: "Email or username already exists" });
    }
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/auth/login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: "email and password required" });
  }
  try {
    const result = await query(`
      SELECT * FROM students WHERE email = $1
    `, [email]);

    if (result.rows.length === 0) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const student = result.rows[0];
    const valid = await bcrypt.compare(password, student.password_hash);
    if (!valid) return res.status(401).json({ error: "Invalid credentials" });

    const token = jwt.sign({ id: student.id, email: student.email }, JWT_SECRET, { expiresIn: "30d" });

    res.json({
      token,
      student: { id: student.id, email: student.email, username: student.username }
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/auth/me", authMiddleware, async (req, res) => {
  try {
    const result = await query(`
      SELECT s.id, s.email, s.username, s.created_at,
             sp.leetcode_handle, sp.codeforces_handle,
             sp.codechef_handle, sp.atcoder_handle, sp.skill_rating
      FROM students s
      LEFT JOIN student_profiles sp ON s.id = sp.student_id
      WHERE s.id = $1
    `, [req.studentId]);

    if (result.rows.length === 0) return res.status(404).json({ error: "Not found" });
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - PROFILE
// ─────────────────────────────────────────────

app.put("/api/profile/handles", authMiddleware, async (req, res) => {
  const { leetcode_handle, codeforces_handle, codechef_handle, atcoder_handle } = req.body;
  try {
    await query(`
      UPDATE student_profiles
      SET leetcode_handle = $1, codeforces_handle = $2,
          codechef_handle = $3, atcoder_handle = $4,
          updated_at = NOW()
      WHERE student_id = $5
    `, [leetcode_handle, codeforces_handle, codechef_handle, atcoder_handle, req.studentId]);

    res.json({ message: "Handles updated successfully" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - CONTESTS
// ─────────────────────────────────────────────

app.get("/api/contests", async (req, res) => {
  try {
    const cached = await cacheGet("contests:all");
    if (cached) return res.json({ contests: cached, cached: true });

    const result = await query(`
      SELECT * FROM contests
      WHERE start_time > NOW()
      ORDER BY start_time ASC
      LIMIT 20
    `);

    const contests = result.rows;
    await cacheSet("contests:all", contests, 1800);
    res.json({ contests, cached: false });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/contests/refresh", async (req, res) => {
  try {
    const contests = await fetchAndStoreContests();
    res.json({ message: "Contests refreshed", count: contests.length });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/contests/:contestId/remind", authMiddleware, async (req, res) => {
  try {
    await query(`
      INSERT INTO contest_reminders (student_id, contest_id)
      VALUES ($1, $2)
      ON CONFLICT (student_id, contest_id) DO NOTHING
    `, [req.studentId, req.params.contestId]);

    res.json({ message: "Reminder set. You will be notified 30 minutes before the contest." });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete("/api/contests/:contestId/remind", authMiddleware, async (req, res) => {
  try {
    await query(`
      DELETE FROM contest_reminders
      WHERE student_id = $1 AND contest_id = $2
    `, [req.studentId, req.params.contestId]);

    res.json({ message: "Reminder removed" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/contests/reminders", authMiddleware, async (req, res) => {
  try {
    const result = await query(`
      SELECT c.*, cr.notified
      FROM contest_reminders cr
      JOIN contests c ON cr.contest_id = c.id
      WHERE cr.student_id = $1
      ORDER BY c.start_time ASC
    `, [req.studentId]);

    res.json({ reminders: result.rows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - STREAK
// ─────────────────────────────────────────────

app.get("/api/streak", authMiddleware, async (req, res) => {
  try {
    const streak = await getStreak(req.studentId);
    res.json(streak);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/streak/log", authMiddleware, async (req, res) => {
  const { platform = "manual" } = req.body;
  try {
    await logActivity(req.studentId, platform);
    const streak = await getStreak(req.studentId);
    res.json({ message: "Activity logged", streak });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - SUBMISSIONS (Bridge to ML)
// ─────────────────────────────────────────────

app.post("/api/submissions", authMiddleware, async (req, res) => {
  const {
    problem_id, problem_title, code,
    language, verdict, time_spent_minutes = 0, platform = "manual"
  } = req.body;

  if (!problem_id || !code || !verdict) {
    return res.status(400).json({ error: "problem_id, code, verdict required" });
  }

  try {
    // Log activity regardless of verdict
    await logActivity(req.studentId, platform);

    // Check if student is struggling and trigger ML
    if (verdict !== "AC") {
      checkAndTriggerAnalysis(
        req.studentId, problem_id, problem_title || problem_id,
        code, language || "python", verdict, time_spent_minutes
      );
    }

    res.json({
      message: verdict === "AC" ? "Accepted! Activity logged." : "Submission recorded. Analyzing your code...",
      verdict
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - SUGGESTIONS (CodeCrux Suggestions Panel)
// ─────────────────────────────────────────────

app.get("/api/suggestions", authMiddleware, async (req, res) => {
  try {
    // Get latest ML suggestions for this student
    const result = await query(`
      SELECT * FROM ml_suggestions
      WHERE student_id = $1
      ORDER BY created_at DESC
      LIMIT 5
    `, [req.studentId]);

    if (result.rows.length === 0) {
      // Fall back to ML service direct query
      try {
        const mlRes = await axios.get(`${ML_URL}/suggestions/${req.studentId}`, { timeout: 10000 });
        return res.json(mlRes.data);
      } catch {
        return res.json({ suggestions: [], message: "No suggestions yet. Keep solving problems!" });
      }
    }

    const latest = result.rows[0];
    const suggestions = typeof latest.suggestions === "string"
      ? JSON.parse(latest.suggestions)
      : latest.suggestions;

    res.json({
      concept_gap: latest.concept_gap,
      tutoring_note: latest.tutoring_note,
      suggestions: suggestions || [],
      generated_at: latest.created_at
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/suggestions/analyze", authMiddleware, async (req, res) => {
  const { problem, submission } = req.body;
  if (!problem || !submission) {
    return res.status(400).json({ error: "problem and submission required" });
  }

  try {
    const mlResult = await callMLAnalyze(req.studentId, problem, submission);
    if (!mlResult) {
      return res.status(503).json({ error: "ML service unavailable" });
    }

    if (mlResult.diagnosis) {
      await query(`
        INSERT INTO ml_suggestions
          (student_id, concept_gap, tutoring_note, suggestions)
        VALUES ($1, $2, $3, $4)
      `, [
        req.studentId,
        mlResult.diagnosis.specific_concept_missing,
        mlResult.diagnosis.tutoring_note,
        JSON.stringify(mlResult.suggestions || [])
      ]);
    }

    res.json(mlResult);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - DASHBOARD
// ─────────────────────────────────────────────

app.get("/api/dashboard", authMiddleware, async (req, res) => {
  try {
    const [streakRes, contestsRes, suggestionsRes, profileRes] = await Promise.all([
      getStreak(req.studentId),
      query(`
        SELECT c.* FROM contests c
        WHERE c.start_time > NOW()
        ORDER BY c.start_time ASC LIMIT 5
      `),
      query(`
        SELECT concept_gap, tutoring_note, created_at
        FROM ml_suggestions
        WHERE student_id = $1
        ORDER BY created_at DESC LIMIT 1
      `, [req.studentId]),
      query(`
        SELECT sp.*, s.username, s.email
        FROM student_profiles sp
        JOIN students s ON sp.student_id = s.id
        WHERE sp.student_id = $1
      `, [req.studentId])
    ]);

    res.json({
      streak: streakRes,
      upcoming_contests: contestsRes.rows,
      latest_suggestion: suggestionsRes.rows[0] || null,
      profile: profileRes.rows[0] || null
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
// ROUTES - HEALTH
// ─────────────────────────────────────────────

app.get("/", (req, res) => {
  res.json({
    service: "CodeCrux Backend",
    status: "running",
    endpoints: {
      auth: ["POST /api/auth/register", "POST /api/auth/login", "GET /api/auth/me"],
      profile: ["PUT /api/profile/handles"],
      contests: ["GET /api/contests", "GET /api/contests/refresh", "POST /api/contests/:id/remind"],
      streak: ["GET /api/streak", "POST /api/streak/log"],
      submissions: ["POST /api/submissions"],
      suggestions: ["GET /api/suggestions", "POST /api/suggestions/analyze"],
      dashboard: ["GET /api/dashboard"]
    }
  });
});
calendarRoutes(app, authMiddleware);
pollerRoutes(app , pool , authMiddleware,pool);
app.get("/health", async (req, res) => {
  const checks = {};
  try { await query("SELECT 1"); checks.postgres = "ok"; }
  catch (e) { checks.postgres = e.message; }
  try { await redisClient.ping(); checks.redis = "ok"; }
  catch (e) { checks.redis = e.message; }
  try { await axios.get(`${ML_URL}/health`, { timeout: 3000 }); checks.ml_service = "ok"; }
  catch { checks.ml_service = "unreachable"; }
  res.json(checks);
});

// ─────────────────────────────────────────────
// STARTUP
// ─────────────────────────────────────────────

async function start() {
  try {
    await redisClient.connect();
    console.log("Redis connected");

    await setupDatabase();

    // Fetch contests on startup
    await fetchAndStoreContests();
    startPoller(pool);

    // Cron: refresh contests every 30 minutes
    cron.schedule("*/30 * * * *", async () => {
      console.log("Cron: refreshing contests...");
      await fetchAndStoreContests();
      
    });

    // Cron: check reminders every minute
    cron.schedule("* * * * *", async () => {
      await checkContestReminders();
    });

    app.listen(PORT, () => {
      console.log(`\nCodeCrux Backend running on http://localhost:${PORT}`);
      console.log(`Health check: http://localhost:${PORT}/health`);
      console.log(`API docs:     http://localhost:${PORT}/\n`);
    });

  } catch (err) {
    console.error("Startup failed:", err);
    process.exit(1);
  }
}

start();
