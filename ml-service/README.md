# codecrux-ml 🧠

> The ML microservice powering CodeCrux's AI diagnosis engine. Analyzes failed competitive programming submissions, identifies the specific knowledge gap, and retrieves targeted practice problems via semantic search.

Part of the [CodeCrux](https://github.com/Praveensajja05/codecrux) project.

---

## What this service does

When a student struggles on a problem, this service:
1. Parses their submitted code using `tree-sitter` (AST analysis)
2. Infers what algorithm they were attempting
3. Diagnoses the **exact** concept they're missing (via Claude API)
4. Generates a Socratic tutoring note anchored to their own code
5. Retrieves the simplest practice problem targeting that gap (via pgvector semantic search)

---

## Tech Stack

- **Python + FastAPI** — REST API service
- **Anthropic Claude API** — Code diagnosis and tutoring note generation
- **sentence-transformers** (`all-MiniLM-L6-v2`) — Problem corpus embeddings
- **pgvector** — Vector similarity search over 112+ problems
- **tree-sitter** — AST-level code parsing

---

## Project Structure

```
codecrux-ml/
├── main.py           # FastAPI app — /analyze, /suggestions endpoints
├── schemas.py        # Pydantic models (DiagnosisResult, etc.)
├── prompts.py        # Claude system prompt + prompt builder
├── embeddings.py     # Problem corpus seeding + embedding generation
├── retrieval.py      # pgvector nearest-neighbor search
├── seed_problems.py  # One-time script to seed the problem corpus
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Diagnose a failed code submission |
| `POST` | `/embed-problem` | Add a problem to the vector corpus |
| `GET` | `/suggestions/{user_id}` | Get suggestions for a user |
| `POST` | `/event` | Receive behavior events from backend |

### Sample Request — `/analyze`

```json
{
  "user_id": "u123",
  "problem_id": "lc-1143",
  "language": "python",
  "code": "def longestCommonSubsequence(self, text1, text2):\n    dp = [0] * len(text2)\n    ..."
}
```

### Sample Response

```json
{
  "intended_approach": "bottom-up tabulation over 1D array",
  "correct_approach": "2D DP table tracking both string indices",
  "gap_type": "wrong_state_definition",
  "specific_concept_missing": "defining DP state over two sequences simultaneously",
  "tutoring_note": "Your dp[] array only tracks position in text2 — but the state needs to encode where you are in both strings at once. What happens to your dp[j] value when text1[i] changes?",
  "suggested_problem": {
    "id": "lc-72",
    "title": "Edit Distance",
    "difficulty": "Medium",
    "reason": "Simplest problem requiring 2D DP state over two sequences"
  }
}
```

---

## Setup

```bash
# Clone
git clone https://github.com/Praveensajja05/codecrux-ml
cd codecrux-ml

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY and DATABASE_URL

# Seed the problem corpus (run once)
python seed_problems.py

# Start the server
uvicorn main:app --reload --port 8001
```

---

## Environment Variables

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/codecrux
```

---

## Related Repos

- [codecrux](https://github.com/Praveensajja05/codecrux) — Project overview & full README
- [codecrux-backend](https://github.com/Praveensajja05/codecrux-backend) — Node.js backend
- [codecrux-frontend](https://github.com/Praveensajja05/codecrux-frontend) — React frontend
