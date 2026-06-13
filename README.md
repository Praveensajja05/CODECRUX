# CODECRUX
# CodeCrux 🧠
## Repositories
- [codecrux-backend](https://github.com/Praveensajja05/codecrux-backend) — Node.js server
- [codecrux-frontend](https://github.com/Praveensajja05/codecrux-frontend) — React app  
- [codecrux-ml](https://github.com/Praveensajja05/codecrux-ml) — Python ML service

> **An AI-powered competitive programming tutor** that aggregates contests from every major platform, tracks your coding streak, and diagnoses *exactly* what you don't understand from your failed submissions — not just "wrong answer", but the specific concept you're missing.

---

## What is CodeCrux?

Most tools tell you *what* you got wrong. CodeCrux tells you *why*.

When you struggle on a problem, CodeCrux's ML engine analyzes your failed code, identifies your specific knowledge gap (e.g., *"you're not maintaining the monotonic invariant when popping from the stack"* — not just *"stack problem"*), generates a Socratic tutoring note anchored to your own code, and surfaces the simplest practice problem that isolates exactly that concept.

It's also a full contest dashboard — one place for Codeforces, LeetCode, CodeChef, AtCoder, and HackerRank, with Google Calendar sync and 30-minute pre-contest notifications.

---

## Features

- **Contest Aggregator** — Live and upcoming contests from Codeforces, LeetCode, CodeChef, AtCoder, HackerRank in a unified feed
- **AI Code Diagnosis** — 5-stage ML pipeline that diagnoses your specific knowledge gap from failed code, not just the symptom
- **Socratic Tutoring Notes** — Personalized 2–4 sentence explanations that reference your own variable names and end with a question to push your thinking
- **Semantic Problem Retrieval** — pgvector-powered search finds the simplest problem isolating your exact missing concept
- **Streak Tracking** — Daily coding activity tracked across all connected platforms
- **Google Calendar Sync** — Contest events written directly to your calendar with 30-minute reminders
- **Push + Email Notifications** — Pre-contest alerts so you never miss a round
- **CodeCrux Suggestions Panel** — Persistent sidebar showing your current weak areas and targeted practice problems

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│   Dashboard │ Contest Feed │ Suggestions │ Progress         │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│               Node.js + Express Backend                     │
│  Auth │ Contest Aggregator │ Streak │ Notifications │ OAuth │
│  PostgreSQL (user data, streaks, contest cache)             │
│  Redis (notification queues, caching)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST (async)
┌──────────────────────▼──────────────────────────────────────┐
│              Python FastAPI — ML Tutor Engine               │
│                                                             │
│  Stage 1: Code ingestion + AST parsing (tree-sitter)        │
│  Stage 2: Intent inference (what the student tried to do)   │
│  Stage 3: Gap diagnosis → structured JSON (Claude API)      │
│  Stage 4: Tutoring note generation (anchored to their code) │
│  Stage 5: Semantic retrieval (pgvector nearest-neighbor)    │
│                                                             │
│  sentence-transformers │ pgvector │ Anthropic Claude API    │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS |
| Backend | Node.js, Express, PostgreSQL, Redis |
| ML Service | Python, FastAPI, sentence-transformers |
| AI / LLM | Anthropic Claude API (`claude-sonnet-4-6`) |
| Vector DB | pgvector (PostgreSQL extension) |
| Code Parsing | tree-sitter |
| Notifications | SendGrid (email), Web Push API |
| Calendar | Google Calendar OAuth 2.0 |
| Deployment | Render (backend), local ML service |

---

## ML Tutor Engine — How It Works

The core of CodeCrux is a 5-stage diagnosis pipeline that runs every time a struggle event is detected (2+ failed submissions, or time spent > 2× median for that difficulty).

### Stage 1 — Code Ingestion
Parses the submitted code using `tree-sitter` to extract structural features: data structures used, loop nesting depth, recursive calls, apparent time complexity. This gives the LLM structured context beyond raw text.

### Stage 2 — Intent Inference
Asks Claude: *"What algorithm is this student trying to implement?"* Separates intent from correctness — understanding what they attempted before judging whether it's right.

### Stage 3 — Gap Diagnosis
Compares intent against the correct approach. Returns structured JSON:

```json
{
  "intended_approach": "bottom-up tabulation over 1D array",
  "correct_approach": "top-down memoization with tree recursion",
  "approach_match": false,
  "gap_type": "wrong_algorithm",
  "specific_concept_missing": "memoizing overlapping subproblems in tree DFS",
  "tutoring_note": "Your dp[] array is indexed by value, but this problem's state space is the tree structure itself...",
  "suggested_concept_path": ["recursion on trees", "top-down memoization", "tree DP"]
}
```

### Stage 4 — Tutoring Note
The `tutoring_note` field is personalized: it references the student's actual variable names and structure, never gives away the solution, and ends with a question. *"Your `visited[]` array is resetting between calls in `dfs()` — what does that mean for nodes you've already computed?"*

### Stage 5 — Semantic Retrieval
Embeds `specific_concept_missing` using `sentence-transformers` (`all-MiniLM-L6-v2`), runs nearest-neighbor search in pgvector against a corpus of 112+ problems, filtered by difficulty range and novelty (problems the student hasn't seen). Returns the **simplest** problem that isolates the exact concept — not the most similar problem.

---

## Problem Corpus

Each problem in the corpus stores:
- Title, statement, difficulty, platform tags
- Optimal solution approach description
- Key concepts required (granular — not "DP" but "interval DP with prefix sums")
- Common wrong approaches and what misconception each reveals
- Sentence embedding vector (768-dim, stored in pgvector)

Embeddings are generated offline using `sentence-transformers` and stored once. Retrieval at inference time is a single vector similarity query.

---

## Project Structure

```
codecrux/
├── frontend/               # React app
│   ├── src/
│   │   ├── components/     # Dashboard, ContestFeed, Suggestions, Progress
│   │   └── pages/
│   └── package.json
│
├── backend/                # Node.js + Express
│   ├── routes/
│   │   ├── auth.js
│   │   ├── contests.js
│   │   ├── calendar.js
│   │   └── notifications.js
│   ├── poller.js           # Contest aggregation cron job
│   └── server.js
│
└── ml/                     # Python FastAPI ML service
    ├── schemas.py          # Pydantic models for DiagnosisResult
    ├── prompts.py          # Diagnosis system prompt + builder
    ├── embeddings.py       # Problem corpus seeding + pgvector
    ├── retrieval.py        # Nearest-neighbor search logic
    └── main.py             # FastAPI app with /analyze, /suggestions endpoints
```

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL with pgvector extension
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone the repo

```bash
git clone https://github.com/Praveensajja05/codecrux
cd codecrux
```

### 2. Backend setup

```bash
cd backend
cp .env.example .env
# Fill in your values in .env
npm install
npm run dev
```

### 3. ML service setup

```bash
cd ml
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed the problem corpus (run once)
python seed_problems.py

# Start the FastAPI server
uvicorn main:app --reload --port 8001
```

### 4. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`, backend at `http://localhost:3000`, ML service at `http://localhost:8001`.

---

## Environment Variables

Copy `.env.example` to `.env` in the `backend/` folder and fill in:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/codecrux

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=your_jwt_secret

# Anthropic (for ML service)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Calendar OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Notifications
SENDGRID_API_KEY=your_sendgrid_api_key
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
```

---

## API Endpoints (ML Service)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Diagnose failed code submission |
| `POST` | `/embed-problem` | Add a problem to the vector corpus |
| `GET` | `/suggestions/{user_id}` | Get cached suggestions for a user |
| `POST` | `/event` | Receive behavior events from backend |

---

## What's Next

- [ ] Browser extension to capture code directly from LeetCode / Codeforces
- [ ] Spaced repetition — resurface weak concepts after 3 days / 1 week / 1 month
- [ ] Expand problem corpus to 5000+ problems (full LeetCode + Codeforces)
- [ ] Progress page with topic mastery graph and predicted rating trajectory
- [ ] Mobile responsive layout
- [ ] Friend streaks and contest leaderboards

---

## Author

**Praveen Sajja** — B.Tech, IIT Indore
[GitHub](https://github.com/Praveensajja05) · [LinkedIn](https://linkedin.com/in/your-profile)

---

*Built with the belief that "wrong answer" is never the real diagnosis.*
