"""
CodeCrux - Expanded Problem Corpus Seeder
-----------------------------------------
Adds 50 new problems to your existing database.
Run this once: python seed_corpus.py

Requirements: same venv as codecrux_ml.py
"""

import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@127.0.0.1:5432/codecrux")

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

NEW_PROBLEMS = [

    # ─── BINARY SEARCH ───────────────────────────────────────────────────────

    {
        "id": "lc-704",
        "platform": "leetcode",
        "title": "Binary Search",
        "statement": "Given an array of integers nums sorted in ascending order and a target integer, write a function to search target in nums. Return the index if found, else return -1.",
        "difficulty_rating": 800,
        "tags": ["array", "binary search"],
        "url": "https://leetcode.com/problems/binary-search/",
        "correct_approach": "Classic binary search. lo=0, hi=n-1. While lo<=hi, mid=(lo+hi)//2. Compare nums[mid] with target.",
        "key_concepts": ["binary search template", "lo hi mid pattern", "termination condition"],
        "common_mistakes": ["off by one on hi initialization", "wrong termination condition lo<hi vs lo<=hi", "infinite loop when lo and hi don't converge"]
    },
    {
        "id": "lc-35",
        "platform": "leetcode",
        "title": "Search Insert Position",
        "statement": "Given a sorted array and a target value, return the index if the target is found. If not, return the index where it would be inserted in order.",
        "difficulty_rating": 900,
        "tags": ["array", "binary search"],
        "url": "https://leetcode.com/problems/search-insert-position/",
        "correct_approach": "Binary search. When not found, lo is the insertion position.",
        "key_concepts": ["binary search insertion point", "leftmost position", "lo as answer when not found"],
        "common_mistakes": ["returning mid instead of lo when not found", "not handling element larger than all in array"]
    },
    {
        "id": "lc-153",
        "platform": "leetcode",
        "title": "Find Minimum in Rotated Sorted Array",
        "statement": "Given a rotated sorted array of unique elements, find the minimum element.",
        "difficulty_rating": 1200,
        "tags": ["array", "binary search"],
        "url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/",
        "correct_approach": "Binary search. Compare nums[mid] with nums[hi] to determine which half the minimum is in.",
        "key_concepts": ["binary search on rotated array", "comparing mid with boundary", "minimum in rotation"],
        "common_mistakes": ["comparing mid with lo instead of hi", "not handling non-rotated case", "wrong boundary update"]
    },
    {
        "id": "lc-4",
        "platform": "leetcode",
        "title": "Median of Two Sorted Arrays",
        "statement": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
        "difficulty_rating": 1900,
        "tags": ["array", "binary search", "divide and conquer"],
        "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/",
        "correct_approach": "Binary search on the smaller array to find the partition point. O(log(min(m,n))).",
        "key_concepts": ["binary search on partition", "median via partition invariant", "handling odd and even total length"],
        "common_mistakes": ["using merge O(m+n) instead of binary search", "wrong partition boundary conditions", "not handling edge cases when one array is empty"]
    },

    # ─── GRAPH ALGORITHMS ────────────────────────────────────────────────────

    {
        "id": "lc-207",
        "platform": "leetcode",
        "title": "Course Schedule",
        "statement": "There are numCourses courses. Some courses have prerequisites. Return true if you can finish all courses.",
        "difficulty_rating": 1400,
        "tags": ["graph", "dfs", "bfs", "topological sort"],
        "url": "https://leetcode.com/problems/course-schedule/",
        "correct_approach": "Detect cycle in directed graph. Use DFS with 3-color marking (white/gray/black) or Kahn's BFS topological sort.",
        "key_concepts": ["cycle detection in directed graph", "3-color DFS", "Kahn's algorithm topological sort"],
        "common_mistakes": ["using visited set only without in-progress tracking", "not detecting back edges", "confusing undirected and directed cycle detection"]
    },
    {
        "id": "lc-210",
        "platform": "leetcode",
        "title": "Course Schedule II",
        "statement": "Return the ordering of courses you should take to finish all courses. If impossible, return empty array.",
        "difficulty_rating": 1500,
        "tags": ["graph", "dfs", "topological sort"],
        "url": "https://leetcode.com/problems/course-schedule-ii/",
        "correct_approach": "Topological sort via DFS postorder or Kahn's BFS. Return postorder reversed.",
        "key_concepts": ["topological sort order", "postorder DFS reversal", "Kahn's BFS with indegree"],
        "common_mistakes": ["returning preorder instead of postorder", "not reversing postorder result", "not handling disconnected components"]
    },
    {
        "id": "lc-743",
        "platform": "leetcode",
        "title": "Network Delay Time",
        "statement": "Given a network of n nodes and travel times, find how long it takes for all nodes to receive a signal sent from node k.",
        "difficulty_rating": 1500,
        "tags": ["graph", "dijkstra", "shortest path", "heap"],
        "url": "https://leetcode.com/problems/network-delay-time/",
        "correct_approach": "Dijkstra's algorithm from source k. Answer is max of all shortest distances.",
        "key_concepts": ["Dijkstra's algorithm", "min heap with distances", "relaxation step"],
        "common_mistakes": ["using BFS instead of Dijkstra for weighted graph", "not initializing distances to infinity", "not checking if node already visited when popped"]
    },
    {
        "id": "lc-684",
        "platform": "leetcode",
        "title": "Redundant Connection",
        "statement": "In a graph that started as a tree with n nodes, one additional edge was added. Find that edge.",
        "difficulty_rating": 1400,
        "tags": ["graph", "union find", "dfs"],
        "url": "https://leetcode.com/problems/redundant-connection/",
        "correct_approach": "Union Find. For each edge, if both nodes already in same component, that edge is redundant.",
        "key_concepts": ["union find with path compression", "cycle detection via union find", "find with rank optimization"],
        "common_mistakes": ["using DFS cycle detection which is harder", "not implementing path compression", "wrong union by rank"]
    },
    {
        "id": "lc-994",
        "platform": "leetcode",
        "title": "Rotting Oranges",
        "statement": "In a grid, 0 is empty, 1 is fresh orange, 2 is rotten. Every minute, fresh oranges adjacent to rotten become rotten. Return minimum minutes until no fresh orange remains.",
        "difficulty_rating": 1300,
        "tags": ["graph", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/rotting-oranges/",
        "correct_approach": "Multi-source BFS starting from all rotten oranges simultaneously. Count minutes.",
        "key_concepts": ["multi-source BFS", "level-by-level BFS for time tracking", "simultaneous spread simulation"],
        "common_mistakes": ["single source BFS missing simultaneous spread", "not counting fresh oranges to verify all rotted", "off by one on minute count"]
    },
    {
        "id": "lc-787",
        "platform": "leetcode",
        "title": "Cheapest Flights Within K Stops",
        "statement": "Find the cheapest price from source to destination with at most k stops.",
        "difficulty_rating": 1600,
        "tags": ["graph", "dp", "bellman-ford", "bfs"],
        "url": "https://leetcode.com/problems/cheapest-flights-within-k-stops/",
        "correct_approach": "Bellman-Ford with k+1 iterations. Or BFS/Dijkstra with state (node, stops_remaining).",
        "key_concepts": ["Bellman-Ford with iteration limit", "state space with stops", "copy prices before each iteration"],
        "common_mistakes": ["using standard Dijkstra ignoring stop limit", "updating prices in-place causing cascading updates in same iteration", "off by one on k stops vs k+1 edges"]
    },

    # ─── BACKTRACKING ────────────────────────────────────────────────────────

    {
        "id": "lc-46",
        "platform": "leetcode",
        "title": "Permutations",
        "statement": "Given an array nums of distinct integers, return all the possible permutations.",
        "difficulty_rating": 1200,
        "tags": ["array", "backtracking"],
        "url": "https://leetcode.com/problems/permutations/",
        "correct_approach": "Backtracking. At each position, try each unused number. Use a used[] boolean array.",
        "key_concepts": ["backtracking template", "used array for tracking", "append and pop pattern"],
        "common_mistakes": ["not removing element on backtrack", "using set instead of ordered tracking", "appending reference instead of copy to result"]
    },
    {
        "id": "lc-78",
        "platform": "leetcode",
        "title": "Subsets",
        "statement": "Given an integer array nums of unique elements, return all possible subsets.",
        "difficulty_rating": 1200,
        "tags": ["array", "backtracking", "bit manipulation"],
        "url": "https://leetcode.com/problems/subsets/",
        "correct_approach": "Backtracking with start index. At each step decide include or exclude current element.",
        "key_concepts": ["subset backtracking with start index", "include exclude decision", "result at every node not just leaf"],
        "common_mistakes": ["only collecting results at leaves", "not using start index causing duplicates", "not copying current path before appending to result"]
    },
    {
        "id": "lc-39",
        "platform": "leetcode",
        "title": "Combination Sum",
        "statement": "Given an array of distinct integers candidates and a target, return all unique combinations that sum to target. Same number may be used unlimited times.",
        "difficulty_rating": 1300,
        "tags": ["array", "backtracking"],
        "url": "https://leetcode.com/problems/combination-sum/",
        "correct_approach": "Backtracking. At each step either use current element again (same index) or move to next.",
        "key_concepts": ["unbounded backtracking", "reusing same element", "pruning when sum exceeds target"],
        "common_mistakes": ["advancing index when element can be reused", "not pruning when sum > target", "generating duplicates by not using start index"]
    },
    {
        "id": "lc-79",
        "platform": "leetcode",
        "title": "Word Search",
        "statement": "Given an m x n grid of characters and a string word, return true if word exists in the grid. Word must be constructed from sequentially adjacent cells.",
        "difficulty_rating": 1500,
        "tags": ["array", "backtracking", "dfs", "matrix"],
        "url": "https://leetcode.com/problems/word-search/",
        "correct_approach": "DFS backtracking from each cell. Mark visited by temporarily changing cell value.",
        "key_concepts": ["grid DFS backtracking", "in-place visited marking", "restore cell on backtrack"],
        "common_mistakes": ["not restoring cell value on backtrack", "not marking cell as visited before recursing", "checking bounds after accessing array"]
    },
    {
        "id": "lc-51",
        "platform": "leetcode",
        "title": "N-Queens",
        "statement": "Place n queens on an n x n chessboard such that no two queens attack each other. Return all distinct solutions.",
        "difficulty_rating": 1700,
        "tags": ["array", "backtracking"],
        "url": "https://leetcode.com/problems/n-queens/",
        "correct_approach": "Backtracking row by row. Track columns, diagonals, and anti-diagonals with sets.",
        "key_concepts": ["queen attack pattern", "diagonal tracking with row-col", "anti-diagonal tracking with row+col"],
        "common_mistakes": ["not tracking diagonals separately", "using 2D board check O(n) instead of sets O(1)", "wrong diagonal formula"]
    },

    # ─── TRIE ────────────────────────────────────────────────────────────────

    {
        "id": "lc-208",
        "platform": "leetcode",
        "title": "Implement Trie (Prefix Tree)",
        "statement": "Implement a trie with insert, search, and startsWith methods.",
        "difficulty_rating": 1400,
        "tags": ["trie", "hash table", "string", "design"],
        "url": "https://leetcode.com/problems/implement-trie-prefix-tree/",
        "correct_approach": "Each node has children dict and is_end flag. Insert char by char. Search checks is_end.",
        "key_concepts": ["trie node structure", "children dictionary", "is_end flag for complete words"],
        "common_mistakes": ["confusing search with startsWith", "not setting is_end on insert", "using array of 26 instead of dict for children"]
    },
    {
        "id": "lc-212",
        "platform": "leetcode",
        "title": "Word Search II",
        "statement": "Given an m x n board of characters and a list of strings words, return all words on the board.",
        "difficulty_rating": 1800,
        "tags": ["trie", "backtracking", "array", "matrix"],
        "url": "https://leetcode.com/problems/word-search-ii/",
        "correct_approach": "Build trie from words. DFS on board tracking trie node. Prune when no trie child matches.",
        "key_concepts": ["trie pruning in DFS", "combining trie with backtracking", "removing found words from trie to avoid duplicates"],
        "common_mistakes": ["naive search for each word separately causing TLE", "not pruning dead trie branches", "duplicate results when word appears multiple times"]
    },

    # ─── HEAP / PRIORITY QUEUE ───────────────────────────────────────────────

    {
        "id": "lc-347",
        "platform": "leetcode",
        "title": "Top K Frequent Elements",
        "statement": "Given an integer array nums and an integer k, return the k most frequent elements.",
        "difficulty_rating": 1200,
        "tags": ["array", "hash table", "heap", "bucket sort"],
        "url": "https://leetcode.com/problems/top-k-frequent-elements/",
        "correct_approach": "Count frequencies with hash map. Use min heap of size k or bucket sort by frequency.",
        "key_concepts": ["min heap of size k", "frequency counting", "bucket sort by frequency O(n)"],
        "common_mistakes": ["using max heap and popping k times O(nlogn)", "not using min heap to maintain size k", "sorting entire frequency map"]
    },
    {
        "id": "lc-295",
        "platform": "leetcode",
        "title": "Find Median from Data Stream",
        "statement": "Design a data structure that supports adding integers and finding the median at any point.",
        "difficulty_rating": 1700,
        "tags": ["heap", "two heaps", "design", "data stream"],
        "url": "https://leetcode.com/problems/find-median-from-data-stream/",
        "correct_approach": "Two heaps: max heap for lower half, min heap for upper half. Balance sizes on each add.",
        "key_concepts": ["two heap median trick", "max heap lower half min heap upper half", "balancing heap sizes"],
        "common_mistakes": ["using single sorted list O(n) insert", "not balancing heaps after each insert", "wrong median formula for even vs odd total"]
    },
    {
        "id": "lc-621",
        "platform": "leetcode",
        "title": "Task Scheduler",
        "statement": "Given a list of tasks with a cooldown n, find the minimum number of intervals needed to finish all tasks.",
        "difficulty_rating": 1500,
        "tags": ["array", "heap", "greedy", "counting"],
        "url": "https://leetcode.com/problems/task-scheduler/",
        "correct_approach": "Greedy with max heap. Always schedule most frequent task available. Fill idle slots.",
        "key_concepts": ["greedy task scheduling", "max heap by frequency", "idle time calculation"],
        "common_mistakes": ["not considering idle slots", "using math formula without understanding derivation", "wrong cooldown tracking"]
    },

    # ─── STRING ALGORITHMS ───────────────────────────────────────────────────

    {
        "id": "lc-3",
        "platform": "leetcode",
        "title": "Longest Substring Without Repeating Characters",
        "statement": "Given a string s, find the length of the longest substring without repeating characters.",
        "difficulty_rating": 1100,
        "tags": ["string", "sliding window", "hash table"],
        "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "correct_approach": "Sliding window with hash map storing last index of each character. Move left pointer on repeat.",
        "key_concepts": ["sliding window with character index map", "moving left pointer on duplicate", "window length calculation"],
        "common_mistakes": ["moving left by 1 instead of jumping past duplicate", "not updating character index after moving left", "using set which loses position information"]
    },
    {
        "id": "lc-5",
        "platform": "leetcode",
        "title": "Longest Palindromic Substring",
        "statement": "Given a string s, return the longest palindromic substring in s.",
        "difficulty_rating": 1300,
        "tags": ["string", "dp", "expand around center"],
        "url": "https://leetcode.com/problems/longest-palindromic-substring/",
        "correct_approach": "Expand around center for each character and each pair. O(n2). Or Manacher's O(n).",
        "key_concepts": ["expand around center technique", "odd and even length palindromes", "center index tracking"],
        "common_mistakes": ["only checking odd length palindromes", "wrong index calculation when expanding", "using O(n3) naive approach"]
    },
    {
        "id": "lc-49",
        "platform": "leetcode",
        "title": "Group Anagrams",
        "statement": "Given an array of strings strs, group the anagrams together.",
        "difficulty_rating": 1100,
        "tags": ["string", "hash table", "sorting"],
        "url": "https://leetcode.com/problems/group-anagrams/",
        "correct_approach": "Use sorted string or character count tuple as hash key. Group strings by key.",
        "key_concepts": ["anagram canonical form", "sorted string as key", "character frequency tuple as key"],
        "common_mistakes": ["comparing each pair O(n2)", "not using immutable key for dict", "sorting each string correctly"]
    },
    {
        "id": "lc-424",
        "platform": "leetcode",
        "title": "Longest Repeating Character Replacement",
        "statement": "Given a string s and integer k, find the longest substring containing the same letter after at most k replacements.",
        "difficulty_rating": 1500,
        "tags": ["string", "sliding window", "hash table"],
        "url": "https://leetcode.com/problems/longest-repeating-character-replacement/",
        "correct_approach": "Sliding window. Track max frequency in window. Window is valid if window_size - max_freq <= k.",
        "key_concepts": ["sliding window with max frequency", "validity condition window_size - max_freq <= k", "max_freq never decreases optimization"],
        "common_mistakes": ["recomputing max frequency on each shrink", "shrinking window when it could stay same size", "not understanding why max_freq monotonically increases"]
    },
    {
        "id": "lc-647",
        "platform": "leetcode",
        "title": "Palindromic Substrings",
        "statement": "Given a string s, return the number of palindromic substrings in it.",
        "difficulty_rating": 1300,
        "tags": ["string", "dp", "expand around center"],
        "url": "https://leetcode.com/problems/palindromic-substrings/",
        "correct_approach": "Expand around each center (n centers for odd, n-1 for even). Count each expansion.",
        "key_concepts": ["expand around center counting", "odd and even centers", "counting during expansion"],
        "common_mistakes": ["using O(n3) triple loop", "missing even length palindromes", "double counting"]
    },

    # ─── DYNAMIC PROGRAMMING ─────────────────────────────────────────────────

    {
        "id": "lc-1143",
        "platform": "leetcode",
        "title": "Longest Common Subsequence",
        "statement": "Given two strings text1 and text2, return the length of their longest common subsequence.",
        "difficulty_rating": 1400,
        "tags": ["string", "dp"],
        "url": "https://leetcode.com/problems/longest-common-subsequence/",
        "correct_approach": "2D DP. dp[i][j] = LCS of text1[:i] and text2[:j]. If chars match, dp[i][j] = dp[i-1][j-1]+1.",
        "key_concepts": ["2D string DP", "LCS recurrence", "match vs no-match transition"],
        "common_mistakes": ["confusing LCS with LCS substring", "wrong recurrence when chars don't match", "off by one in string indexing"]
    },
    {
        "id": "lc-300",
        "platform": "leetcode",
        "title": "Longest Increasing Subsequence",
        "statement": "Given an integer array nums, return the length of the longest strictly increasing subsequence.",
        "difficulty_rating": 1400,
        "tags": ["array", "dp", "binary search"],
        "url": "https://leetcode.com/problems/longest-increasing-subsequence/",
        "correct_approach": "DP O(n2): dp[i] = max LIS ending at i. Or patience sorting with binary search O(nlogn).",
        "key_concepts": ["LIS dp recurrence", "patience sorting tails array", "binary search for insertion position"],
        "common_mistakes": ["returning max of dp array not dp[n-1]", "wrong patience sorting update", "not understanding tails array meaning"]
    },
    {
        "id": "lc-72",
        "platform": "leetcode",
        "title": "Edit Distance",
        "statement": "Given two strings word1 and word2, return the minimum number of operations (insert, delete, replace) to convert word1 to word2.",
        "difficulty_rating": 1600,
        "tags": ["string", "dp"],
        "url": "https://leetcode.com/problems/edit-distance/",
        "correct_approach": "2D DP. dp[i][j] = min ops to convert word1[:i] to word2[:j]. Three transitions for insert/delete/replace.",
        "key_concepts": ["edit distance recurrence", "three operation transitions", "base case initialization with empty string"],
        "common_mistakes": ["wrong base case initialization", "confusing which string is source and target", "not handling empty string base cases"]
    },
    {
        "id": "lc-139",
        "platform": "leetcode",
        "title": "Word Break",
        "statement": "Given a string s and a dictionary wordDict, return true if s can be segmented into dictionary words.",
        "difficulty_rating": 1400,
        "tags": ["string", "dp", "trie", "memoization"],
        "url": "https://leetcode.com/problems/word-break/",
        "correct_approach": "DP. dp[i] = can s[:i] be segmented. For each i, check all j<i where dp[j] is true and s[j:i] in dict.",
        "key_concepts": ["string segmentation dp", "dp[i] as reachability", "using set for O(1) word lookup"],
        "common_mistakes": ["exponential recursion without memoization", "O(n) list lookup instead of set", "wrong dp transition direction"]
    },
    {
        "id": "lc-152",
        "platform": "leetcode",
        "title": "Maximum Product Subarray",
        "statement": "Given an integer array nums, find a subarray that has the largest product, and return the product.",
        "difficulty_rating": 1400,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/maximum-product-subarray/",
        "correct_approach": "Track both max and min product ending at each position. Negative number flips max and min.",
        "key_concepts": ["tracking both max and min", "negative number flips sign", "swap max min on negative"],
        "common_mistakes": ["only tracking max product missing negative flip", "not initializing result before loop", "wrong swap logic"]
    },
    {
        "id": "lc-309",
        "platform": "leetcode",
        "title": "Best Time to Buy and Sell Stock with Cooldown",
        "statement": "Given stock prices, find max profit with cooldown (after selling must wait one day before buying).",
        "difficulty_rating": 1600,
        "tags": ["array", "dp", "state machine"],
        "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/",
        "correct_approach": "State machine DP. Three states: held, sold, rest. Transition between states each day.",
        "key_concepts": ["state machine dp", "held sold rest states", "state transition equations"],
        "common_mistakes": ["not modeling cooldown as separate state", "wrong state transitions", "using single variable missing state information"]
    },

    # ─── TWO POINTERS ────────────────────────────────────────────────────────

    {
        "id": "lc-11",
        "platform": "leetcode",
        "title": "Container With Most Water",
        "statement": "Given n non-negative integers representing vertical lines, find two lines that together with the x-axis form a container that holds the most water.",
        "difficulty_rating": 1200,
        "tags": ["array", "two pointers", "greedy"],
        "url": "https://leetcode.com/problems/container-with-most-water/",
        "correct_approach": "Two pointers from both ends. Always move the pointer with smaller height inward.",
        "key_concepts": ["two pointer greedy", "moving shorter line inward", "area calculation width times min height"],
        "common_mistakes": ["moving taller pointer inward", "not understanding why greedy works", "O(n2) brute force"]
    },
    {
        "id": "lc-15",
        "platform": "leetcode",
        "title": "3Sum",
        "statement": "Given an integer array nums, return all triplets that sum to zero. The solution must not contain duplicate triplets.",
        "difficulty_rating": 1300,
        "tags": ["array", "two pointers", "sorting"],
        "url": "https://leetcode.com/problems/3sum/",
        "correct_approach": "Sort. For each i, use two pointers on remaining array. Skip duplicates carefully.",
        "key_concepts": ["sort then two pointer", "duplicate skipping for all three indices", "two pointer for pair sum"],
        "common_mistakes": ["not skipping duplicates for outer loop", "not skipping duplicates for inner two pointers", "using set to deduplicate which is slower"]
    },
    {
        "id": "lc-42",
        "platform": "leetcode",
        "title": "Trapping Rain Water",
        "statement": "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
        "difficulty_rating": 1600,
        "tags": ["array", "two pointers", "stack", "dp"],
        "url": "https://leetcode.com/problems/trapping-rain-water/",
        "correct_approach": "Two pointers. Track left_max and right_max. Water at each position is min(left_max, right_max) - height.",
        "key_concepts": ["two pointer water trapping", "left max right max arrays", "min of two maxes determines water level"],
        "common_mistakes": ["using prefix/suffix arrays O(n) space when O(1) possible", "wrong formula for water at position", "not understanding why min of maxes works"]
    },

    # ─── MATH AND BIT MANIPULATION ───────────────────────────────────────────

    {
        "id": "lc-268",
        "platform": "leetcode",
        "title": "Missing Number",
        "statement": "Given an array nums containing n distinct numbers in range [0, n], return the only number in the range that is missing.",
        "difficulty_rating": 900,
        "tags": ["array", "math", "bit manipulation", "sorting"],
        "url": "https://leetcode.com/problems/missing-number/",
        "correct_approach": "XOR all indices and values. Or use Gauss sum n*(n+1)/2 minus array sum.",
        "key_concepts": ["Gauss sum formula", "XOR cancellation", "expected minus actual sum"],
        "common_mistakes": ["using O(n) space set", "overflow on large n with sum approach", "wrong XOR range"]
    },
    {
        "id": "lc-191",
        "platform": "leetcode",
        "title": "Number of 1 Bits",
        "statement": "Write a function that takes an unsigned integer and returns the number of 1 bits (Hamming weight).",
        "difficulty_rating": 900,
        "tags": ["bit manipulation"],
        "url": "https://leetcode.com/problems/number-of-1-bits/",
        "correct_approach": "n & (n-1) clears the lowest set bit. Count how many times until n=0.",
        "key_concepts": ["n & n-1 trick clears lowest bit", "Brian Kernighan algorithm", "bit counting"],
        "common_mistakes": ["using n & 1 and shifting which is slower", "not handling unsigned integers correctly", "infinite loop on negative numbers in some languages"]
    },
    {
        "id": "lc-338",
        "platform": "leetcode",
        "title": "Counting Bits",
        "statement": "Given an integer n, return an array ans of length n+1 such that ans[i] is the number of 1s in binary representation of i.",
        "difficulty_rating": 1000,
        "tags": ["dp", "bit manipulation"],
        "url": "https://leetcode.com/problems/counting-bits/",
        "correct_approach": "DP. dp[i] = dp[i >> 1] + (i & 1). Number of bits in i equals bits in i//2 plus last bit.",
        "key_concepts": ["bit dp recurrence", "right shift relation", "last bit extraction with AND 1"],
        "common_mistakes": ["using O(nlogn) by counting bits for each number", "wrong recurrence relation", "not seeing the pattern"]
    },
    {
        "id": "lc-136",
        "platform": "leetcode",
        "title": "Single Number",
        "statement": "Given a non-empty array where every element appears twice except one, find that single one.",
        "difficulty_rating": 900,
        "tags": ["array", "bit manipulation"],
        "url": "https://leetcode.com/problems/single-number/",
        "correct_approach": "XOR all numbers. Pairs cancel out (a XOR a = 0). Result is the single number.",
        "key_concepts": ["XOR self-cancellation", "XOR commutativity", "XOR with 0 identity"],
        "common_mistakes": ["using hash map O(n) space when O(1) possible", "not understanding XOR properties", "using sum approach which needs extra math"]
    },

    # ─── STACK AND QUEUE ─────────────────────────────────────────────────────

    {
        "id": "lc-20",
        "platform": "leetcode",
        "title": "Valid Parentheses",
        "statement": "Given a string containing just '(', ')', '{', '}', '[', ']', determine if the input string is valid.",
        "difficulty_rating": 900,
        "tags": ["string", "stack"],
        "url": "https://leetcode.com/problems/valid-parentheses/",
        "correct_approach": "Stack. Push open brackets. On close bracket, check if top matches. Return stack empty at end.",
        "key_concepts": ["stack for bracket matching", "matching pairs dict", "empty stack check at end"],
        "common_mistakes": ["not checking if stack is empty before popping", "not returning False when stack non-empty at end", "using counter instead of stack losing order info"]
    },
    {
        "id": "lc-155",
        "platform": "leetcode",
        "title": "Min Stack",
        "statement": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.",
        "difficulty_rating": 1100,
        "tags": ["stack", "design"],
        "url": "https://leetcode.com/problems/min-stack/",
        "correct_approach": "Maintain auxiliary min stack. Push current min alongside each element.",
        "key_concepts": ["auxiliary min stack", "pushing current min with each element", "O(1) getMin"],
        "common_mistakes": ["only storing global min which breaks on pop", "using separate min variable instead of stack", "not pushing to min stack on every push"]
    },
    {
        "id": "lc-739",
        "platform": "leetcode",
        "title": "Daily Temperatures",
        "statement": "Given an array of daily temperatures, return an array where each element is how many days until a warmer temperature.",
        "difficulty_rating": 1300,
        "tags": ["array", "stack", "monotonic stack"],
        "url": "https://leetcode.com/problems/daily-temperatures/",
        "correct_approach": "Monotonic decreasing stack of indices. When current temp > stack top temp, pop and compute distance.",
        "key_concepts": ["monotonic stack for next greater element", "storing indices not values", "distance calculation on pop"],
        "common_mistakes": ["storing temperatures instead of indices", "not processing remaining stack at end", "wrong distance formula"]
    },

    # ─── CODEFORCES STYLE ────────────────────────────────────────────────────

    {
        "id": "cf-1A",
        "platform": "codeforces",
        "title": "Theatre Square",
        "statement": "A rectangular plaza of dimensions n x m needs to be paved with square slabs of size a x a. Slabs may not be cut. How many slabs are needed?",
        "difficulty_rating": 800,
        "tags": ["math"],
        "url": "https://codeforces.com/problemset/problem/1/A",
        "correct_approach": "ceil(n/a) * ceil(m/a). Use integer ceiling division: (n + a - 1) // a.",
        "key_concepts": ["ceiling division formula", "integer arithmetic ceiling", "2D tiling"],
        "common_mistakes": ["using float division and round causing precision errors", "forgetting ceiling on both dimensions", "integer overflow on large inputs"]
    },
    {
        "id": "cf-71A",
        "platform": "codeforces",
        "title": "Way Too Long Words",
        "statement": "If a word is longer than 10 characters, abbreviate it as first_letter + count_of_middle_letters + last_letter.",
        "difficulty_rating": 800,
        "tags": ["string", "implementation"],
        "url": "https://codeforces.com/problemset/problem/71/A",
        "correct_approach": "Check len(word) > 10. If so, output word[0] + str(len(word)-2) + word[-1].",
        "key_concepts": ["string indexing", "conditional abbreviation", "length check"],
        "common_mistakes": ["wrong count of middle letters", "not handling words exactly 10 chars", "string concatenation with int without str()"]
    },
    {
        "id": "cf-158B",
        "platform": "codeforces",
        "title": "Taxi",
        "statement": "Groups of 1-4 people need taxis that seat 4. Find minimum number of taxis needed.",
        "difficulty_rating": 1000,
        "tags": ["math", "greedy", "implementation"],
        "url": "https://codeforces.com/problemset/problem/158/B",
        "correct_approach": "Pair groups of 3 with groups of 1. Pair groups of 2. Use ceiling for remainder.",
        "key_concepts": ["greedy pairing", "groups of 3 absorb groups of 1", "ceiling division for remainder"],
        "common_mistakes": ["not pairing 3s with 1s first", "wrong handling of remaining 1s and 2s", "not using ceiling for final count"]
    },
    {
        "id": "cf-231A",
        "platform": "codeforces",
        "title": "Team",
        "statement": "Three friends each predict outcomes of n problems. For each problem, if at least 2 friends are confident, count it as solvable. Find how many problems they'll solve.",
        "difficulty_rating": 900,
        "tags": ["brute force", "implementation"],
        "url": "https://codeforces.com/problemset/problem/231/A",
        "correct_approach": "For each problem count sum of three predictions. If sum >= 2, increment answer.",
        "key_concepts": ["simple threshold counting", "reading multiple inputs per line", "majority vote"],
        "common_mistakes": ["wrong input parsing", "using OR instead of counting >= 2", "off by one in loop"]
    },
    {
        "id": "cf-263A",
        "platform": "codeforces",
        "title": "Beautiful Matrix",
        "statement": "Given a 5x5 matrix, find the minimum moves to place the 0 element to the center position.",
        "difficulty_rating": 1000,
        "tags": ["implementation", "math"],
        "url": "https://codeforces.com/problemset/problem/263/A",
        "correct_approach": "Find position of 0. Manhattan distance to center (2,2) is abs(r-2) + abs(c-2).",
        "key_concepts": ["Manhattan distance", "finding element position in matrix", "target position calculation"],
        "common_mistakes": ["using Euclidean distance", "wrong center index in 0-indexed vs 1-indexed", "searching incorrectly in 2D array"]
    },
    {
        "id": "cf-282A",
        "platform": "codeforces",
        "title": "Cows and Primitive Roots",
        "statement": "Given n, find the number of integers in [1, n-1] that are primitive roots modulo n.",
        "difficulty_rating": 1200,
        "tags": ["math", "number theory"],
        "url": "https://codeforces.com/problemset/problem/284/A",
        "correct_approach": "Use Euler's totient function. Count numbers coprime to totient(n).",
        "key_concepts": ["Euler totient function", "primitive root counting", "coprimality check"],
        "common_mistakes": ["brute force checking all powers", "not understanding primitive root definition", "wrong totient computation"]
    },

    # ─── INTERVALS ───────────────────────────────────────────────────────────

    {
        "id": "lc-56",
        "platform": "leetcode",
        "title": "Merge Intervals",
        "statement": "Given an array of intervals, merge all overlapping intervals and return the result.",
        "difficulty_rating": 1200,
        "tags": ["array", "sorting", "intervals"],
        "url": "https://leetcode.com/problems/merge-intervals/",
        "correct_approach": "Sort by start. For each interval, if it overlaps with last merged, extend end. Else add new.",
        "key_concepts": ["sort by start time", "overlap check current start <= last end", "extending end with max"],
        "common_mistakes": ["not sorting first", "wrong overlap condition", "not taking max of ends when merging"]
    },
    {
        "id": "lc-57",
        "platform": "leetcode",
        "title": "Insert Interval",
        "statement": "Given a sorted non-overlapping list of intervals and a new interval, insert it and merge if necessary.",
        "difficulty_rating": 1300,
        "tags": ["array", "intervals"],
        "url": "https://leetcode.com/problems/insert-interval/",
        "correct_approach": "Three phases: add all intervals ending before new start, merge overlapping, add remaining.",
        "key_concepts": ["three phase interval insertion", "non-overlap condition", "merge overlapping with new interval"],
        "common_mistakes": ["not handling all three phases separately", "wrong comparison for before and after regions", "off by one in overlap detection"]
    },
    {
        "id": "lc-435",
        "platform": "leetcode",
        "title": "Non-overlapping Intervals",
        "statement": "Given an array of intervals, return the minimum number of intervals to remove to make the rest non-overlapping.",
        "difficulty_rating": 1400,
        "tags": ["array", "sorting", "greedy", "intervals"],
        "url": "https://leetcode.com/problems/non-overlapping-intervals/",
        "correct_approach": "Greedy. Sort by end time. Keep interval with earliest end. Remove overlapping ones.",
        "key_concepts": ["greedy interval scheduling", "sort by end time", "keep earliest ending interval"],
        "common_mistakes": ["sorting by start instead of end", "not understanding why earliest end is greedy choice", "counting kept instead of removed"]
    },

    # ─── MATRIX ──────────────────────────────────────────────────────────────

    {
        "id": "lc-73",
        "platform": "leetcode",
        "title": "Set Matrix Zeroes",
        "statement": "Given an m x n matrix, if an element is 0, set its entire row and column to 0. Do it in-place.",
        "difficulty_rating": 1200,
        "tags": ["array", "matrix", "hash table"],
        "url": "https://leetcode.com/problems/set-matrix-zeroes/",
        "correct_approach": "Use first row and column as markers. Check and handle first row/col separately.",
        "key_concepts": ["in-place marker using first row/col", "two-pass approach", "handling first row and col edge case"],
        "common_mistakes": ["marking while iterating causing cascade", "using O(mn) extra space", "not handling first row/col separately as markers"]
    },
    {
        "id": "lc-54",
        "platform": "leetcode",
        "title": "Spiral Matrix",
        "statement": "Given an m x n matrix, return all elements in spiral order.",
        "difficulty_rating": 1200,
        "tags": ["array", "matrix", "simulation"],
        "url": "https://leetcode.com/problems/spiral-matrix/",
        "correct_approach": "Track boundaries: top, bottom, left, right. Shrink after each direction traversal.",
        "key_concepts": ["boundary shrinking", "four direction traversal order", "boundary update after each pass"],
        "common_mistakes": ["not shrinking boundaries", "wrong traversal order", "processing already visited cells"]
    },
    {
        "id": "lc-48",
        "platform": "leetcode",
        "title": "Rotate Image",
        "statement": "Given an n x n matrix, rotate it 90 degrees clockwise in-place.",
        "difficulty_rating": 1200,
        "tags": ["array", "matrix", "math"],
        "url": "https://leetcode.com/problems/rotate-image/",
        "correct_approach": "Transpose then reverse each row. Or rotate layer by layer.",
        "key_concepts": ["transpose then reverse", "in-place rotation identity", "layer by layer rotation"],
        "common_mistakes": ["using extra matrix O(n2) space", "wrong transpose formula", "reversing columns instead of rows after transpose"]
    },

    # ─── LINKED LIST ─────────────────────────────────────────────────────────

    {
        "id": "lc-141",
        "platform": "leetcode",
        "title": "Linked List Cycle",
        "statement": "Given head of a linked list, determine if the linked list has a cycle.",
        "difficulty_rating": 900,
        "tags": ["linked list", "two pointers", "Floyd cycle"],
        "url": "https://leetcode.com/problems/linked-list-cycle/",
        "correct_approach": "Floyd's cycle detection. Slow pointer moves 1 step, fast moves 2. They meet iff cycle exists.",
        "key_concepts": ["Floyd's tortoise and hare", "slow fast pointer", "cycle detection O(1) space"],
        "common_mistakes": ["using hash set O(n) space", "wrong null check order causing NullPointer", "not checking fast.next before fast.next.next"]
    },
    {
        "id": "lc-19",
        "platform": "leetcode",
        "title": "Remove Nth Node From End of List",
        "statement": "Given the head of a linked list, remove the nth node from the end of the list and return its head.",
        "difficulty_rating": 1100,
        "tags": ["linked list", "two pointers"],
        "url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/",
        "correct_approach": "Two pointers with n gap. When fast reaches end, slow is at node before target.",
        "key_concepts": ["two pointer with fixed gap", "dummy head node", "one-pass solution"],
        "common_mistakes": ["two-pass solution when one-pass is cleaner", "not using dummy head for removing first node", "wrong gap initialization"]
    },
    {
        "id": "lc-142",
        "platform": "leetcode",
        "title": "Linked List Cycle II",
        "statement": "Given a linked list, return the node where the cycle begins. If no cycle, return null.",
        "difficulty_rating": 1500,
        "tags": ["linked list", "two pointers", "Floyd cycle"],
        "url": "https://leetcode.com/problems/linked-list-cycle-ii/",
        "correct_approach": "Floyd detection to find meeting point. Then move one pointer to head, both at same speed, they meet at cycle start.",
        "key_concepts": ["Floyd cycle entry finding", "mathematical proof of cycle start", "two phase detection"],
        "common_mistakes": ["returning meeting point instead of cycle start", "not understanding the math behind phase 2", "using hash set which misses the point"]
    },
]


def seed_new_problems():
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print(f"Seeding {len(NEW_PROBLEMS)} new problems...")
    success = 0
    skipped = 0

    for p in NEW_PROBLEMS:
        embed_text = (
            f"competitive programming: {p['title']}. "
            f"{p['statement']} "
            f"Key concepts: {', '.join(p.get('key_concepts', []))}. "
            f"Tags: {', '.join(p.get('tags', []))}"
        )
        embedding = model.encode(embed_text).tolist()

        cur.execute("""
            INSERT INTO problems
                (id, platform, title, statement, difficulty_rating, tags, url,
                 correct_approach, key_concepts, common_mistakes, embedding)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
                embedding = EXCLUDED.embedding,
                key_concepts = EXCLUDED.key_concepts,
                correct_approach = EXCLUDED.correct_approach
        """, (
            p["id"], p["platform"], p["title"], p["statement"],
            p["difficulty_rating"], p["tags"], p["url"],
            p["correct_approach"], p["key_concepts"], p["common_mistakes"],
            str(embedding)
        ))
        print(f"  Seeded: {p['title']}")
        success += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nDone. {success} problems seeded successfully.")

    # Verify total count
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM problems;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"Total problems in database: {total}")


if __name__ == "__main__":
    seed_new_problems()
