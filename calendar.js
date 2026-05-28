/**
 * CodeCrux - Google Calendar Integration
 */

const { google } = require("googleapis");
const dotenv     = require("dotenv");

dotenv.config();

let pool;

async function query(text, params) {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

async function setupCalendarTable() {
  await query(`
    CREATE TABLE IF NOT EXISTS calendar_tokens (
      student_id    BIGINT PRIMARY KEY,
      access_token  TEXT,
      refresh_token TEXT,
      expiry_date   BIGINT,
      connected_at  TIMESTAMPTZ DEFAULT NOW()
    );
  `);
  await query(`
    CREATE TABLE IF NOT EXISTS calendar_events (
      id                BIGSERIAL PRIMARY KEY,
      student_id        BIGINT,
      contest_id        TEXT,
      calendar_event_id TEXT,
      created_at        TIMESTAMPTZ DEFAULT NOW()
    );
  `);
  console.log("Calendar tokens table ready.");
}

function getOAuth2Client() {
  return new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
  );
}

async function getAuthUrl(studentId) {
  const oauth2Client = getOAuth2Client();
  const url = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: ["https://www.googleapis.com/auth/calendar.events"],
    state: String(studentId),
    prompt: "consent"
  });
  return url;
}

async function exchangeCodeForTokens(code, studentId) {
  const oauth2Client = getOAuth2Client();
  const { tokens } = await oauth2Client.getToken(code);

  await query(`
    INSERT INTO calendar_tokens
      (student_id, access_token, refresh_token, expiry_date)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT (student_id) DO UPDATE SET
      access_token  = EXCLUDED.access_token,
      refresh_token = EXCLUDED.refresh_token,
      expiry_date   = EXCLUDED.expiry_date,
      connected_at  = NOW()
  `, [studentId, tokens.access_token, tokens.refresh_token, tokens.expiry_date]);

  return tokens;
}

async function getStudentCalendarClient(studentId) {
  const res = await query(`SELECT * FROM calendar_tokens WHERE student_id = $1`, [studentId]);

  if (res.rows.length === 0) {
    throw new Error("Google Calendar not connected. Please connect first.");
  }

  const tokenRow = res.rows[0];
  const oauth2Client = getOAuth2Client();

  oauth2Client.setCredentials({
    access_token:  tokenRow.access_token,
    refresh_token: tokenRow.refresh_token,
    expiry_date:   tokenRow.expiry_date
  });

  oauth2Client.on("tokens", async (tokens) => {
    if (tokens.access_token) {
      await query(`
        UPDATE calendar_tokens SET access_token = $1, expiry_date = $2 WHERE student_id = $3
      `, [tokens.access_token, tokens.expiry_date, studentId]);
    }
  });

  return google.calendar({ version: "v3", auth: oauth2Client });
}

async function addContestToCalendar(studentId, contest) {
  const calendar = await getStudentCalendarClient(studentId);

  const startTime = new Date(contest.start_time);
  const endTime   = new Date(startTime.getTime() + (contest.duration_mins || 120) * 60 * 1000);

  const event = {
    summary: `🏆 ${contest.title}`,
    description: `Platform: ${contest.platform}\nContest URL: ${contest.url}\n\nAdded by CodeCrux`,
    start: { dateTime: startTime.toISOString(), timeZone: "Asia/Kolkata" },
    end:   { dateTime: endTime.toISOString(),   timeZone: "Asia/Kolkata" },
    reminders: {
      useDefault: false,
      overrides: [
        { method: "email", minutes: 30 },
        { method: "popup", minutes: 30 }
      ]
    },
    colorId: "6"
  };

  const response = await calendar.events.insert({ calendarId: "primary", resource: event });

  await query(`
    INSERT INTO calendar_events (student_id, contest_id, calendar_event_id)
    VALUES ($1, $2, $3) ON CONFLICT DO NOTHING
  `, [studentId, contest.id, response.data.id]);

  return response.data;
}

async function removeContestFromCalendar(studentId, contestId) {
  const calendar = await getStudentCalendarClient(studentId);

  const res = await query(`
    SELECT calendar_event_id FROM calendar_events WHERE student_id = $1 AND contest_id = $2
  `, [studentId, contestId]);

  if (res.rows.length === 0) throw new Error("No calendar event found for this contest.");

  await calendar.events.delete({ calendarId: "primary", eventId: res.rows[0].calendar_event_id });

  await query(`DELETE FROM calendar_events WHERE student_id = $1 AND contest_id = $2`, [studentId, contestId]);
}

async function isCalendarConnected(studentId) {
  const res = await query(`SELECT student_id FROM calendar_tokens WHERE student_id = $1`, [studentId]);
  return res.rows.length > 0;
}

function calendarRoutes(app, authMiddleware, dbPool) {
  pool = dbPool;

  setupCalendarTable().catch(err => console.log("Calendar table setup error:", err.message));

  app.get("/api/calendar/auth", authMiddleware, async (req, res) => {
    try {
      const url = await getAuthUrl(req.studentId);
      res.json({ url });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.get("/api/calendar/callback", async (req, res) => {
    const { code, state } = req.query;
    if (!code || !state) return res.status(400).send("Missing code or state");
    try {
      await exchangeCodeForTokens(code, state);
      res.send(`
        <html>
          <body style="font-family:sans-serif;text-align:center;padding:40px;background:#1a1a2e;color:white;">
            <h2 style="color:#7DF9C0">Google Calendar Connected!</h2>
            <p>You can close this tab and return to CodeCrux.</p>
            <script>setTimeout(() => window.close(), 2000);</script>
          </body>
        </html>
      `);
    } catch (err) {
      res.status(500).send(`Error: ${err.message}`);
    }
  });

  app.get("/api/calendar/status", authMiddleware, async (req, res) => {
    try {
      const connected = await isCalendarConnected(req.studentId);
      res.json({ connected });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/calendar/add/:contestId", authMiddleware, async (req, res) => {
    try {
      const contestRes = await query(`SELECT * FROM contests WHERE id = $1`, [req.params.contestId]);
      if (contestRes.rows.length === 0) return res.status(404).json({ error: "Contest not found" });
      const event = await addContestToCalendar(req.studentId, contestRes.rows[0]);
      res.json({ message: "Contest added to your Google Calendar with 30 minute reminder.", event_id: event.id, event_link: event.htmlLink });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.delete("/api/calendar/remove/:contestId", authMiddleware, async (req, res) => {
    try {
      await removeContestFromCalendar(req.studentId, req.params.contestId);
      res.json({ message: "Contest removed from your Google Calendar." });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/calendar/sync-all", authMiddleware, async (req, res) => {
    try {
      const contestsRes = await query(`SELECT * FROM contests WHERE start_time > NOW() ORDER BY start_time ASC`);
      const results = [];
      for (const contest of contestsRes.rows) {
        try {
          const event = await addContestToCalendar(req.studentId, contest);
          results.push({ contest: contest.title, status: "added", link: event.htmlLink });
        } catch (err) {
          results.push({ contest: contest.title, status: "failed", error: err.message });
        }
      }
      res.json({ message: `Synced ${results.filter(r => r.status === "added").length} contests to Google Calendar.`, results });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  console.log("Calendar routes mounted.");
}

module.exports = { calendarRoutes };
