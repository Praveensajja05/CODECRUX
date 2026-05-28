/**
 * CodeCrux - Platform Activity Poller
 * -------------------------------------
 * Watches student submissions on Codeforces and LeetCode.
 * Detects struggling (multiple WA on same problem).
 * Creates a nudge notification prompting student to paste code.
 *
 * Add to server.js:
 *   const { startPoller } = require("./poller");
 *   startPoller(pool);
 */

const axios = require("axios");
const cron  = require("node-cron");

// ─────────────────────────────────────────────
// DATABASE HELPERS
// ─────────────────────────────────────────────

async function query(pool, text, params) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

async function setupPollerTables(pool) {
  await query(pool, `
    CREATE TABLE IF NOT EXISTS platform_submissions (
      id              BIGSERIAL PRIMARY KEY,
      student_id      BIGINT NOT NULL,
      platform        TEXT NOT NULL,
      problem_id      TEXT NOT NULL,
      problem_name    TEXT NOT NULL,
      problem_url     TEXT,
      verdict         TEXT NOT NULL,
      language        TEXT,
      submitted_at    TIMESTAMPTZ NOT NULL,
      fetched_at      TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(student_id, platform, problem_id, submitted_at)
    );
  `);

  await query(pool, `
    CREATE TABLE IF NOT EXISTS struggle_notifications (
      id              BIGSERIAL PRIMARY KEY,
      student_id      BIGINT NOT NULL,
      platform        TEXT NOT NULL,
      problem_id      TEXT NOT NULL,
      problem_name    TEXT NOT NULL,
      problem_url     TEXT,
      failed_count    INTEGER DEFAULT 0,
      seen            BOOLEAN DEFAULT FALSE,
      dismissed       BOOLEAN DEFAULT FALSE,
      created_at      TIMESTAMPTZ DEFAULT NOW(),
      UNIQUE(student_id, platform, problem_id)
    );
  `);

  console.log("Poller tables ready.");
}

// ─────────────────────────────────────────────
// CODEFORCES POLLER
// ─────────────────────────────────────────────

async function fetchCodeforcesSubmissions(handle) {
  try {
    const res = await axios.get(
      `https://codeforces.com/api/user.status?handle=${handle}&from=1&count=50`,
      { timeout: 10000 }
    );

    if (res.data.status !== "OK") return [];

    return res.data.result.map(s => ({
      platform:     "codeforces",
      problem_id:   `${s.problem.contestId}${s.problem.index}`,
      problem_name: s.problem.name,
      problem_url:  `https://codeforces.com/contest/${s.problem.contestId}/problem/${s.problem.index}`,
      verdict:      s.verdict,
      language:     s.programmingLanguage,
      submitted_at: new Date(s.creationTimeSeconds * 1000).toISOString(),
    }));
  } catch (err) {
    console.log(`Codeforces fetch failed for ${handle}: ${err.message}`);
    return [];
  }
}

// ─────────────────────────────────────────────
// LEETCODE POLLER
// ─────────────────────────────────────────────

async function fetchLeetcodeSubmissions(username) {
  try {
    const res = await axios.post(
      "https://leetcode.com/graphql",
      {
        query: `
          query recentSubmissions($username: String!) {
            recentSubmissionList(username: $username, limit: 50) {
              title
              titleSlug
              timestamp
              statusDisplay
              lang
            }
          }
        `,
        variables: { username }
      },
      {
        headers: { "Content-Type": "application/json" },
        timeout: 10000
      }
    );

    const submissions = res.data?.data?.recentSubmissionList || [];

    return submissions.map(s => ({
      platform:     "leetcode",
      problem_id:   s.titleSlug,
      problem_name: s.title,
      problem_url:  `https://leetcode.com/problems/${s.titleSlug}/`,
      verdict:      s.statusDisplay,
      language:     s.lang,
      submitted_at: new Date(parseInt(s.timestamp) * 1000).toISOString(),
    }));
  } catch (err) {
    console.log(`LeetCode fetch failed for ${username}: ${err.message}`);
    return [];
  }
}

// ─────────────────────────────────────────────
// STRUGGLE DETECTOR
// ─────────────────────────────────────────────

function detectStruggling(submissions) {
  // Group by problem
  const problemMap = {};

  for (const sub of submissions) {
    const key = sub.problem_id;
    if (!problemMap[key]) {
      problemMap[key] = {
        problem_id:   sub.problem_id,
        problem_name: sub.problem_name,
        problem_url:  sub.problem_url,
        platform:     sub.platform,
        verdicts:     [],
        latest:       sub.submitted_at,
      };
    }
    problemMap[key].verdicts.push(sub.verdict);
  }

  const struggling = [];

  for (const problem of Object.values(problemMap)) {
    const wrongAnswers = problem.verdicts.filter(v =>
      v === "Wrong Answer" ||
      v === "WRONG_ANSWER" ||
      v === "Time Limit Exceeded" ||
      v === "TIME_LIMIT_EXCEEDED" ||
      v === "Runtime Error" ||
      v === "RUNTIME_ERROR"
    ).length;

    const hasAccepted = problem.verdicts.some(v =>
      v === "Accepted" || v === "OK"
    );

    // Struggling = 2+ failures with no accepted solution
    if (wrongAnswers >= 2 && !hasAccepted) {
      struggling.push({
        ...problem,
        failed_count: wrongAnswers,
      });
    }
  }

  return struggling;
}

// ─────────────────────────────────────────────
// MAIN POLL FUNCTION
// ─────────────────────────────────────────────

async function pollStudent(pool, student) {
  const { id: studentId, leetcode_handle, codeforces_handle } = student;
  let totalNew = 0;

  // Fetch from both platforms
  const allSubmissions = [];

  if (codeforces_handle) {
    const cfSubs = await fetchCodeforcesSubmissions(codeforces_handle);
    allSubmissions.push(...cfSubs);
  }

  if (leetcode_handle) {
    const lcSubs = await fetchLeetcodeSubmissions(leetcode_handle);
    allSubmissions.push(...lcSubs);
  }

  if (allSubmissions.length === 0) return 0;

  // Store new submissions
  for (const sub of allSubmissions) {
    try {
      await query(pool, `
        INSERT INTO platform_submissions
          (student_id, platform, problem_id, problem_name, problem_url, verdict, language, submitted_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (student_id, platform, problem_id, submitted_at) DO NOTHING
      `, [
        studentId, sub.platform, sub.problem_id, sub.problem_name,
        sub.problem_url, sub.verdict, sub.language, sub.submitted_at
      ]);
      totalNew++;
    } catch {}
  }

  // Detect struggling
  const struggling = detectStruggling(allSubmissions);

  for (const problem of struggling) {
    try {
      await query(pool, `
        INSERT INTO struggle_notifications
          (student_id, platform, problem_id, problem_name, problem_url, failed_count)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (student_id, platform, problem_id) DO UPDATE SET
          failed_count = EXCLUDED.failed_count,
          seen = FALSE
      `, [
        studentId, problem.platform, problem.problem_id,
        problem.problem_name, problem.problem_url, problem.failed_count
      ]);

      console.log(`Struggle detected: ${student.username} on ${problem.problem_name} (${problem.failed_count} failures)`);
    } catch {}
  }

  return totalNew;
}

async function pollAllStudents(pool) {
  console.log("Polling platform activity for all students...");

  const res = await query(pool, `
    SELECT s.id, s.username,
           sp.leetcode_handle, sp.codeforces_handle
    FROM students s
    JOIN student_profiles sp ON s.id = sp.student_id
    WHERE sp.leetcode_handle IS NOT NULL
       OR sp.codeforces_handle IS NOT NULL
  `);

  const students = res.rows;
  console.log(`Polling ${students.length} students...`);

  for (const student of students) {
    await pollStudent(pool, student);
  }

  console.log("Polling complete.");
}

// ─────────────────────────────────────────────
// EXPRESS ROUTES
// ─────────────────────────────────────────────

function pollerRoutes(app, pool, authMiddleware) {

  // Get struggle notifications for logged in student
  app.get("/api/notifications", authMiddleware, async (req, res) => {
    try {
      const result = await query(pool, `
        SELECT * FROM struggle_notifications
        WHERE student_id = $1
          AND dismissed = FALSE
        ORDER BY created_at DESC
        LIMIT 10
      `, [req.studentId]);

      res.json({ notifications: result.rows });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Mark notification as seen
  app.put("/api/notifications/:id/seen", authMiddleware, async (req, res) => {
    try {
      await query(pool, `
        UPDATE struggle_notifications
        SET seen = TRUE
        WHERE id = $1 AND student_id = $2
      `, [req.params.id, req.studentId]);
      res.json({ message: "Marked as seen" });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Dismiss notification
  app.put("/api/notifications/:id/dismiss", authMiddleware, async (req, res) => {
    try {
      await query(pool, `
        UPDATE struggle_notifications
        SET dismissed = TRUE
        WHERE id = $1 AND student_id = $2
      `, [req.params.id, req.studentId]);
      res.json({ message: "Dismissed" });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Get recent submissions from all platforms
  app.get("/api/activity", authMiddleware, async (req, res) => {
    try {
      const result = await query(pool, `
        SELECT platform, problem_name, problem_url, verdict, language, submitted_at
        FROM platform_submissions
        WHERE student_id = $1
        ORDER BY submitted_at DESC
        LIMIT 20
      `, [req.studentId]);

      res.json({ submissions: result.rows });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  // Manual trigger poll for current student
  app.post("/api/activity/sync", authMiddleware, async (req, res) => {
    try {
      const profileRes = await query(pool, `
        SELECT s.id, s.username, sp.leetcode_handle, sp.codeforces_handle
        FROM students s
        JOIN student_profiles sp ON s.id = sp.student_id
        WHERE s.id = $1
      `, [req.studentId]);

      if (profileRes.rows.length === 0) {
        return res.status(404).json({ error: "Profile not found" });
      }

      const student = profileRes.rows[0];

      if (!student.leetcode_handle && !student.codeforces_handle) {
        return res.status(400).json({ error: "No platform handles set. Add your handles in profile settings." });
      }

      await pollStudent(pool, student);

      // Return updated notifications
      const notifRes = await query(pool, `
        SELECT * FROM struggle_notifications
        WHERE student_id = $1 AND dismissed = FALSE
        ORDER BY created_at DESC
      `, [req.studentId]);

      res.json({
        message: "Activity synced successfully",
        notifications: notifRes.rows
      });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  console.log("Poller routes mounted.");
}

// ─────────────────────────────────────────────
// START POLLER
// ─────────────────────────────────────────────

function startPoller(pool) {
  setupPollerTables(pool).then(() => {
    // Poll every 15 minutes
    cron.schedule("*/15 * * * *", async () => {
      try {
        await pollAllStudents(pool);
      } catch (err) {
        console.log("Poller error:", err.message);
      }
    });

    console.log("Platform activity poller started. Runs every 15 minutes.");
  });
}

module.exports = { startPoller, pollerRoutes, pollAllStudents };
