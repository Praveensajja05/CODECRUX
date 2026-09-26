"""
CodeCrux ML Tutor Engine - Complete Single File
------------------------------------------------
Requirements:
    pip install fastapi uvicorn google-generativeai psycopg2-binary redis pydantic python-dotenv httpx sentence-transformers asyncpg

Environment variables (.env file):
    GEMINI_API_KEY=your_key_here
    DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/codecrux
    REDIS_URL=redis://localhost:6379
"""

import os
import json
import asyncio
import hashlib
from enum import Enum
from typing import Optional

import redis
import psycopg2
from groq import Groq
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
DATABASE_URL    = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/codecrux")
REDIS_URL       = os.getenv("REDIS_URL", "redis://localhost:6379")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="CodeCrux Tutor Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────

class GapType(str, Enum):
    WRONG_ALGORITHM     = "wrong_algorithm"
    CORRECT_ALGO_BROKEN = "correct_algo_broken_impl"
    EDGE_CASE_BLINDNESS = "edge_case_blindness"
    COMPLEXITY_ISSUE    = "complexity_issue"
    CONCEPTUAL_GAP      = "conceptual_gap_no_pattern"
    PATTERN_RECOGNITION = "pattern_recognition_failure"

class ImplementationError(BaseModel):
    location: str
    description: str
    error_class: str

class DiagnosisResult(BaseModel):
    intended_approach: str
    correct_approach: str
    approach_match: bool
    implementation_errors: list[ImplementationError] = []
    gap_type: GapType
    specific_concept_missing: str
    tutoring_note: str
    confidence: float
    suggested_concept_path: list[str] = []

class AnalyzeRequest(BaseModel):
    user_id: str
    problem: dict
    submission: dict
    user_context: dict = {}

class EventRequest(BaseModel):
    user_id: str
    type: str
    problem_id: Optional[str] = None
    payload: dict = {}

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_db():
    return psycopg2.connect(DATABASE_URL)

def setup_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id               TEXT PRIMARY KEY,
            platform         TEXT NOT NULL,
            title            TEXT NOT NULL,
            statement        TEXT NOT NULL,
            difficulty_rating INTEGER,
            tags             TEXT[],
            url              TEXT,
            correct_approach TEXT,
            key_concepts     TEXT[],
            common_mistakes  TEXT[],
            embedding        vector(384),
            created_at       TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            TEXT PRIMARY KEY,
            skill_rating  INTEGER DEFAULT 1200,
            weak_topics   TEXT[],
            created_at    TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_attempts (
            id              BIGSERIAL PRIMARY KEY,
            user_id         TEXT NOT NULL,
            problem_id      TEXT,
            code            TEXT,
            language        TEXT,
            verdict         TEXT,
            time_spent_min  INTEGER,
            attempt_number  INTEGER DEFAULT 1,
            diagnosis       JSONB,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            id          BIGSERIAL PRIMARY KEY,
            user_id     TEXT NOT NULL,
            event_type  TEXT NOT NULL,
            problem_id  TEXT,
            payload     JSONB,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id          BIGSERIAL PRIMARY KEY,
            user_id     TEXT NOT NULL,
            problem_id  TEXT,
            reason      TEXT,
            concept     TEXT,
            score       FLOAT,
            seen        BOOLEAN DEFAULT FALSE,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database tables created successfully.")


# ─────────────────────────────────────────────
# PROBLEM CORPUS SEED DATA
# ─────────────────────────────────────────────

SEED_PROBLEMS = [
    {
        "id": "lc-1",
        "platform": "leetcode",
        "title": "Two Sum",
        "statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "difficulty_rating": 800,
        "tags": ["array", "hash table"],
        "url": "https://leetcode.com/problems/two-sum/",
        "correct_approach": "Use a hash map to store complement of each number. O(n) time.",
        "key_concepts": ["hash map lookup", "complement pattern"],
        "common_mistakes": ["using nested loops O(n2)", "not handling duplicate indices"]
    },
    {
        "id": "lc-21",
        "platform": "leetcode",
        "title": "Merge Two Sorted Lists",
        "statement": "Merge two sorted linked lists and return it as a sorted list.",
        "difficulty_rating": 900,
        "tags": ["linked list", "recursion"],
        "url": "https://leetcode.com/problems/merge-two-sorted-lists/",
        "correct_approach": "Iterative with dummy head node or recursive comparison.",
        "key_concepts": ["dummy head node", "pointer manipulation"],
        "common_mistakes": ["losing reference to head", "not handling null termination"]
    },
    {
        "id": "lc-53",
        "platform": "leetcode",
        "title": "Maximum Subarray",
        "statement": "Given an integer array nums, find the subarray with the largest sum and return its sum.",
        "difficulty_rating": 1000,
        "tags": ["array", "dp", "divide and conquer"],
        "url": "https://leetcode.com/problems/maximum-subarray/",
        "correct_approach": "Kadane's algorithm. Track current sum and global max. O(n).",
        "key_concepts": ["Kadane's algorithm", "local vs global maximum"],
        "common_mistakes": ["resetting sum incorrectly", "not initializing max to first element"]
    },
    {
        "id": "lc-70",
        "platform": "leetcode",
        "title": "Climbing Stairs",
        "statement": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "difficulty_rating": 900,
        "tags": ["dp", "math", "memoization"],
        "url": "https://leetcode.com/problems/climbing-stairs/",
        "correct_approach": "dp[i] = dp[i-1] + dp[i-2]. Fibonacci pattern.",
        "key_concepts": ["fibonacci dp", "bottom-up tabulation", "overlapping subproblems"],
        "common_mistakes": ["recursive without memoization causing TLE", "wrong base cases"]
    },
    {
        "id": "lc-104",
        "platform": "leetcode",
        "title": "Maximum Depth of Binary Tree",
        "statement": "Given the root of a binary tree, return its maximum depth.",
        "difficulty_rating": 900,
        "tags": ["tree", "dfs", "bfs", "recursion"],
        "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/",
        "correct_approach": "DFS: return 1 + max(depth(left), depth(right)). Base case: null returns 0.",
        "key_concepts": ["tree dfs recursion", "base case for null node"],
        "common_mistakes": ["forgetting base case", "returning depth without adding 1 for current node"]
    },
    {
        "id": "lc-124",
        "platform": "leetcode",
        "title": "Binary Tree Maximum Path Sum",
        "statement": "A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. Given the root of a binary tree, return the maximum path sum of any non-empty path.",
        "difficulty_rating": 1600,
        "tags": ["tree", "dfs", "dp"],
        "url": "https://leetcode.com/problems/binary-tree-maximum-path-sum/",
        "correct_approach": "DFS returning max gain through one child. Track global max including left+node+right path.",
        "key_concepts": ["tree dp with global state", "returning local value while tracking global max", "memoizing tree dfs with nonlocal"],
        "common_mistakes": ["not considering path through root", "returning both children sum to parent", "missing nonlocal global tracker"]
    },
    {
        "id": "lc-200",
        "platform": "leetcode",
        "title": "Number of Islands",
        "statement": "Given an m x n 2D binary grid which represents a map of 1s (land) and 0s (water), return the number of islands.",
        "difficulty_rating": 1200,
        "tags": ["graph", "dfs", "bfs", "union find"],
        "url": "https://leetcode.com/problems/number-of-islands/",
        "correct_approach": "DFS/BFS from each unvisited land cell, mark visited. Count DFS calls.",
        "key_concepts": ["grid dfs", "visited marking", "connected components"],
        "common_mistakes": ["not marking visited causing infinite loop", "counting cells instead of islands"]
    },
    {
        "id": "lc-206",
        "platform": "leetcode",
        "title": "Reverse Linked List",
        "statement": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
        "difficulty_rating": 900,
        "tags": ["linked list", "recursion"],
        "url": "https://leetcode.com/problems/reverse-linked-list/",
        "correct_approach": "Iterative with prev/curr pointers or recursive.",
        "key_concepts": ["three pointer reversal", "prev curr next pattern"],
        "common_mistakes": ["losing next pointer before reassignment", "not returning prev at end"]
    },
    {
        "id": "lc-322",
        "platform": "leetcode",
        "title": "Coin Change",
        "statement": "Given an array of coins and an amount, return the fewest number of coins needed to make up that amount.",
        "difficulty_rating": 1400,
        "tags": ["dp", "bfs"],
        "url": "https://leetcode.com/problems/coin-change/",
        "correct_approach": "Bottom-up DP. dp[i] = min coins to make amount i. dp[i] = min(dp[i], dp[i-coin]+1).",
        "key_concepts": ["unbounded knapsack dp", "bottom-up 1D dp", "initialization with infinity"],
        "common_mistakes": ["wrong initialization", "greedy approach which fails for some inputs", "not handling amount=0 base case"]
    },
    {
        "id": "lc-416",
        "platform": "leetcode",
        "title": "Partition Equal Subset Sum",
        "statement": "Given an integer array nums, return true if you can partition the array into two subsets such that the sum of the elements in both subsets is equal.",
        "difficulty_rating": 1500,
        "tags": ["dp", "array"],
        "url": "https://leetcode.com/problems/partition-equal-subset-sum/",
        "correct_approach": "0/1 knapsack DP. dp[j] = can we make sum j using subset of nums.",
        "key_concepts": ["0/1 knapsack", "subset sum dp", "boolean dp table"],
        "common_mistakes": ["using unbounded knapsack instead of 0/1", "iterating inner loop forward instead of backward"]
    },
    {
        "id": "lc-84",
        "platform": "leetcode",
        "title": "Largest Rectangle in Histogram",
        "statement": "Given an array of integers heights representing the histogram bar heights, return the area of the largest rectangle in the histogram.",
        "difficulty_rating": 1700,
        "tags": ["array", "stack", "monotonic stack"],
        "url": "https://leetcode.com/problems/largest-rectangle-in-histogram/",
        "correct_approach": "Monotonic increasing stack. Pop when current bar is shorter, compute area.",
        "key_concepts": ["monotonic stack invariant", "stack-based area computation", "sentinel values"],
        "common_mistakes": ["not maintaining monotonic invariant", "wrong width calculation on pop", "missing final stack cleanup"]
    },
    {
        "id": "lc-297",
        "platform": "leetcode",
        "title": "Serialize and Deserialize Binary Tree",
        "statement": "Design an algorithm to serialize and deserialize a binary tree.",
        "difficulty_rating": 1700,
        "tags": ["tree", "dfs", "bfs", "design"],
        "url": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/",
        "correct_approach": "Preorder DFS with null markers. Use queue for deserialization.",
        "key_concepts": ["preorder serialization", "null marker encoding", "queue-based tree reconstruction"],
        "common_mistakes": ["not handling null nodes", "wrong delimiter parsing", "inorder which is not reconstructable uniquely"]
    },
    {
        "id": "lc-239",
        "platform": "leetcode",
        "title": "Sliding Window Maximum",
        "statement": "Given an array nums and a sliding window of size k, return the max values in each window.",
        "difficulty_rating": 1600,
        "tags": ["array", "queue", "sliding window", "monotonic deque"],
        "url": "https://leetcode.com/problems/sliding-window-maximum/",
        "correct_approach": "Monotonic decreasing deque. Store indices. Remove out-of-window elements from front.",
        "key_concepts": ["monotonic deque", "sliding window with deque", "index-based window boundary"],
        "common_mistakes": ["using max heap O(nlogn) instead of deque O(n)", "storing values instead of indices", "not removing expired elements"]
    },
    {
        "id": "lc-307",
        "platform": "leetcode",
        "title": "Range Sum Query - Mutable",
        "statement": "Given an integer array nums, handle multiple queries: update a value, and compute the sum of elements between indices left and right inclusive.",
        "difficulty_rating": 1500,
        "tags": ["segment tree", "binary indexed tree", "array"],
        "url": "https://leetcode.com/problems/range-sum-query-mutable/",
        "correct_approach": "Segment tree or Binary Indexed Tree (Fenwick tree) for O(logn) update and query.",
        "key_concepts": ["segment tree build and update", "range query with segment tree", "BIT Fenwick tree"],
        "common_mistakes": ["using prefix sum which breaks on update", "wrong segment tree indexing", "off by one in tree size"]
    },
    {
        "id": "lc-543",
        "platform": "leetcode",
        "title": "Diameter of Binary Tree",
        "statement": "Given the root of a binary tree, return the length of the diameter of the tree.",
        "difficulty_rating": 1100,
        "tags": ["tree", "dfs"],
        "url": "https://leetcode.com/problems/diameter-of-binary-tree/",
        "correct_approach": "DFS returning height. At each node update global diameter = left_height + right_height.",
        "key_concepts": ["tree dfs returning height", "global state in tree recursion", "diameter vs height distinction"],
        "common_mistakes": ["confusing diameter with height", "not updating global max at each node", "returning diameter instead of height from dfs"]
    },
    {
        "id": "lc-76",
        "platform": "leetcode",
        "title": "Minimum Window Substring",
        "statement": "Given two strings s and t, return the minimum window substring of s such that every character in t is included in the window.",
        "difficulty_rating": 1600,
        "tags": ["string", "sliding window", "hash table"],
        "url": "https://leetcode.com/problems/minimum-window-substring/",
        "correct_approach": "Sliding window with two pointers. Expand right until valid, shrink left while valid.",
        "key_concepts": ["sliding window two pointer", "frequency map with formed counter", "window validity tracking"],
        "common_mistakes": ["not tracking formed count correctly", "shrinking before window is valid", "off by one in result substring"]
    },
    {
        "id": "lc-23",
        "platform": "leetcode",
        "title": "Merge K Sorted Lists",
        "statement": "You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.",
        "difficulty_rating": 1500,
        "tags": ["linked list", "heap", "divide and conquer"],
        "url": "https://leetcode.com/problems/merge-k-sorted-lists/",
        "correct_approach": "Min heap of size k. Push first node of each list, pop min, push next node of that list.",
        "key_concepts": ["min heap for k-way merge", "heap with custom comparator", "priority queue pattern"],
        "common_mistakes": ["naive O(nk) merging", "not pushing next node after popping", "heap comparison on ListNode without key"]
    },
    {
        "id": "lc-62",
        "platform": "leetcode",
        "title": "Unique Paths",
        "statement": "A robot is on an m x n grid. It can only move either down or right. How many possible unique paths are from top-left to bottom-right?",
        "difficulty_rating": 1100,
        "tags": ["dp", "math", "combinatorics"],
        "url": "https://leetcode.com/problems/unique-paths/",
        "correct_approach": "dp[i][j] = dp[i-1][j] + dp[i][j-1]. Base case: first row and column are all 1.",
        "key_concepts": ["2D grid dp", "boundary initialization", "path counting dp"],
        "common_mistakes": ["wrong boundary initialization", "not initializing first row/col to 1", "recursive without memoization"]
    },
    {
        "id": "lc-33",
        "platform": "leetcode",
        "title": "Search in Rotated Sorted Array",
        "statement": "Given a rotated sorted array nums and an integer target, return the index of target or -1 if not found.",
        "difficulty_rating": 1400,
        "tags": ["array", "binary search"],
        "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
        "correct_approach": "Modified binary search. Determine which half is sorted, then check if target is in that half.",
        "key_concepts": ["binary search on rotated array", "identifying sorted half", "two condition binary search"],
        "common_mistakes": ["not identifying which half is sorted", "using linear search instead of binary", "wrong boundary conditions"]
    },
    {
        "id": "lc-146",
        "platform": "leetcode",
        "title": "LRU Cache",
        "statement": "Design a data structure that follows the Least Recently Used cache constraint.",
        "difficulty_rating": 1500,
        "tags": ["hash table", "linked list", "design"],
        "url": "https://leetcode.com/problems/lru-cache/",
        "correct_approach": "Doubly linked list + hash map. O(1) get and put. Move accessed node to front.",
        "key_concepts": ["doubly linked list with sentinel nodes", "hash map to node pointer", "O(1) delete and insert"],
        "common_mistakes": ["using OrderedDict without understanding internals", "not updating on get", "wrong pointer updates on delete"]
    },
]


def seed_problems():
    conn = get_db()
    cur = conn.cursor()

    print(f"Seeding {len(SEED_PROBLEMS)} problems...")

    for p in SEED_PROBLEMS:
        # Generate embedding from title + statement + concepts
        embed_text = (
            f"competitive programming: {p['title']}. "
            f"{p['statement']} "
            f"Key concepts: {', '.join(p.get('key_concepts', []))}. "
            f"Tags: {', '.join(p.get('tags', []))}"
        )
        embedding = embedding_model.encode(embed_text).tolist()

        cur.execute("""
            INSERT INTO problems
                (id, platform, title, statement, difficulty_rating, tags, url,
                 correct_approach, key_concepts, common_mistakes, embedding)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                key_concepts = EXCLUDED.key_concepts
        """, (
            p["id"], p["platform"], p["title"], p["statement"],
            p["difficulty_rating"], p["tags"], p["url"],
            p["correct_approach"], p["key_concepts"], p["common_mistakes"],
            str(embedding)
        ))
        print(f"  Seeded: {p['title']}")

    conn.commit()
    cur.close()
    conn.close()
    print("Problem corpus seeded successfully.")


# ─────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────

DIAGNOSIS_SYSTEM_PROMPT = """
You are an expert competitive programming coach performing precise diagnostic analysis of a student's failed code submission.

Your job is NOT to solve the problem. Your job is to identify exactly what the student does not understand.

Rules:
1. Separate intent from correctness. Understand what the student was TRYING to do first, then evaluate correctness.
2. Be maximally specific about the missing concept. "Dynamic programming" is not a diagnosis. "Student is not recognizing that dp[i] depends on both dp[i-1] and dp[i-2] simultaneously" is a diagnosis.
3. Reference the student's actual variable names and code structure in your diagnosis.
4. Never give the solution. The tutoring_note should push toward insight, not hand it over. End with a question.
5. The specific_concept_missing field drives problem retrieval — it must be a precise learnable concept, not a symptom.

Return ONLY valid JSON. No markdown, no preamble, no explanation outside JSON.

JSON schema:
{
  "intended_approach": "string - what algorithm the student was trying",
  "correct_approach": "string - what the problem actually requires and why",
  "approach_match": true/false,
  "implementation_errors": [
    {
      "location": "string - which function/line using student's variable names",
      "description": "string - what is wrong",
      "error_class": "string - e.g. wrong base case, missing visited set"
    }
  ],
  "gap_type": "one of: wrong_algorithm | correct_algo_broken_impl | edge_case_blindness | complexity_issue | conceptual_gap_no_pattern | pattern_recognition_failure",
  "specific_concept_missing": "string - single precise concept e.g. 'maintaining nonlocal global max in tree DFS while returning local path gain'",
  "tutoring_note": "string - 2-4 sentences anchored to student's code, ends with a question",
  "confidence": 0.0 to 1.0,
  "suggested_concept_path": ["prerequisite concept", "intermediate", "target concept"]
}
""".strip()


def build_diagnosis_prompt(problem, submission):
    return f"""
Diagnose this student's failed submission.

PROBLEM
Title: {problem.get('title')}
Difficulty: {problem.get('difficulty', 'unknown')}
Tags: {', '.join(problem.get('tags', []))}
Statement: {problem.get('statement')}
Expected approach: {problem.get('correct_approach_hint', 'not provided')}

STUDENT SUBMISSION
Language: {submission.get('language', 'python')}
Verdict: {submission.get('verdict', 'Wrong Answer')}
Failed test info: {submission.get('failed_test_info', 'not provided')}
Time spent: {submission.get('time_spent_minutes', 0)} minutes
Prior attempts: {submission.get('prior_attempts', 1)}

Code:
{submission.get('code', '')}

Produce the diagnosis JSON now.
""".strip()


# ─────────────────────────────────────────────
# CORE ML FUNCTIONS
# ─────────────────────────────────────────────

def run_diagnosis(problem: dict, submission: dict) -> DiagnosisResult:
    prompt = build_diagnosis_prompt(problem, submission)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)

    # Normalize gap_type
    gap_map = {
        "wrong_algorithm": GapType.WRONG_ALGORITHM,
        "correct_algo_broken_impl": GapType.CORRECT_ALGO_BROKEN,
        "edge_case_blindness": GapType.EDGE_CASE_BLINDNESS,
        "complexity_issue": GapType.COMPLEXITY_ISSUE,
        "conceptual_gap_no_pattern": GapType.CONCEPTUAL_GAP,
        "pattern_recognition_failure": GapType.PATTERN_RECOGNITION,
    }
    data["gap_type"] = gap_map.get(data.get("gap_type"), GapType.CONCEPTUAL_GAP)

    errors = [ImplementationError(**e) for e in data.get("implementation_errors", [])]
    data["implementation_errors"] = errors

    return DiagnosisResult(**data)


def get_suggestions(diagnosis: DiagnosisResult, user_id: str, top_k: int = 5) -> list[dict]:
    query_text = (
        f"competitive programming problem requiring: {diagnosis.specific_concept_missing}. "
        f"Concept path: {' -> '.join(diagnosis.suggested_concept_path)}"
    )
    query_vector = embedding_model.encode(query_text).tolist()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id, p.title, p.platform, p.difficulty_rating,
            p.tags, p.url, p.key_concepts,
            1 - (p.embedding <=> %s::vector) AS similarity
        FROM problems p
        WHERE p.id NOT IN (
            SELECT problem_id FROM user_attempts
            WHERE user_id = %s AND verdict = 'AC'
        )
        ORDER BY p.embedding <=> %s::vector
        LIMIT %s
    """, (str(query_vector), user_id, str(query_vector), top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "problem_id": row[0],
            "title": row[1],
            "platform": row[2],
            "difficulty": row[3],
            "tags": row[4],
            "url": row[5],
            "key_concepts": row[6],
            "similarity_score": round(float(row[7]), 3),
            "why": f"Practices '{diagnosis.specific_concept_missing}' in isolation.",
        }
        for row in rows
    ]


def save_attempt(user_id: str, problem_id: str, submission: dict, diagnosis: DiagnosisResult):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_attempts
            (user_id, problem_id, code, language, verdict, time_spent_min, diagnosis)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        problem_id,
        submission.get("code"),
        submission.get("language"),
        submission.get("verdict"),
        submission.get("time_spent_minutes", 0),
        json.dumps(diagnosis.model_dump())
    ))
    conn.commit()
    cur.close()
    conn.close()


def ensure_user(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (id) VALUES (%s)
        ON CONFLICT (id) DO NOTHING
    """, (user_id,))
    conn.commit()
    cur.close()
    conn.close()


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "CodeCrux Tutor Engine",
        "status": "running",
        "endpoints": ["/analyze", "/suggestions/{user_id}", "/event", "/problems"]
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    ensure_user(req.user_id)

    # Cache check
    cache_key = f"diagnosis:{req.user_id}:{hashlib.md5(req.submission.get('code','').encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    if cached:
        return {**json.loads(cached), "cached": True}

    # Run diagnosis
    try:
        diagnosis = run_diagnosis(req.problem, req.submission)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")

    # Get suggestions only if confident
    suggestions = []
    if diagnosis.confidence >= 0.6:
        try:
            suggestions = get_suggestions(diagnosis, req.user_id)
        except Exception as e:
            print(f"Suggestion retrieval failed: {e}")

    # Save attempt
    try:
        save_attempt(req.user_id, req.problem.get("id", "unknown"), req.submission, diagnosis)
    except Exception as e:
        print(f"Save attempt failed: {e}")

    result = {
        "diagnosis": diagnosis.model_dump(),
        "suggestions": suggestions,
        "cached": False
    }

    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result


@app.get("/suggestions/{user_id}")
def get_user_suggestions(user_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            ua.diagnosis,
            ua.created_at,
            p.title as problem_title
        FROM user_attempts ua
        LEFT JOIN problems p ON ua.problem_id = p.id
        WHERE ua.user_id = %s
          AND ua.diagnosis IS NOT NULL
        ORDER BY ua.created_at DESC
        LIMIT 10
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return {"suggestions": [], "message": "No analysis run yet for this user."}

    latest_diagnosis_data = rows[0][0]
    if isinstance(latest_diagnosis_data, str):
        latest_diagnosis_data = json.loads(latest_diagnosis_data)

    diagnosis = DiagnosisResult(**latest_diagnosis_data)
    suggestions = get_suggestions(diagnosis, user_id)

    return {
        "user_id": user_id,
        "based_on_problem": rows[0][2],
        "concept_gap": diagnosis.specific_concept_missing,
        "tutoring_note": diagnosis.tutoring_note,
        "suggestions": suggestions,
        "history_count": len(rows)
    }


@app.post("/event")
def ingest_event(req: EventRequest):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_events (user_id, event_type, problem_id, payload)
        VALUES (%s, %s, %s, %s)
    """, (req.user_id, req.type, req.problem_id, json.dumps(req.payload)))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}


@app.get("/problems")
def list_problems():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, platform, difficulty_rating, tags, url
        FROM problems ORDER BY difficulty_rating
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "count": len(rows),
        "problems": [
            {
                "id": r[0], "title": r[1], "platform": r[2],
                "difficulty": r[3], "tags": r[4], "url": r[5]
            }
            for r in rows
        ]
    }


@app.get("/health")
def health():
    checks = {}
    try:
        conn = get_db()
        conn.close()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = str(e)
    try:
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = str(e)
    checks["groq"] = "configured" if os.getenv("GROQ_API_KEY") else "missing key"
    return checks


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    print("Setting up database...")
    setup_database()
    print("Seeding problem corpus...")
    seed_problems()
    print("CodeCrux Tutor Engine ready.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("codecrux_ml:app", host="0.0.0.0", port=8001, reload=True)
