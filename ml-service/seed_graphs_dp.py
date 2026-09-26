"""
CodeCrux - Graph and DP Deep Corpus Seeder
------------------------------------------
Adds 40 more problems focused on Graphs and DP.
Run AFTER seed_corpus.py: python seed_graphs_dp.py
"""

import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@127.0.0.1:5432/codecrux")

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

GRAPH_DP_PROBLEMS = [

    # ═══════════════════════════════════════════════════════════════
    # GRAPHS - BEGINNER
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-733",
        "platform": "leetcode",
        "title": "Flood Fill",
        "statement": "An image is represented as a 2D array. Starting from pixel (sr, sc), flood fill all connected same-color pixels with a new color.",
        "difficulty_rating": 900,
        "tags": ["graph", "dfs", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/flood-fill/",
        "correct_approach": "DFS or BFS from starting pixel. Change color of each connected pixel with original color.",
        "key_concepts": ["grid DFS flood fill", "original color tracking", "avoiding revisit of already filled cells"],
        "common_mistakes": ["infinite loop when new color equals original color", "not storing original color before changing", "checking wrong neighbors"]
    },
    {
        "id": "lc-695",
        "platform": "leetcode",
        "title": "Max Area of Island",
        "statement": "Given a binary matrix, find the maximum area of an island (connected group of 1s).",
        "difficulty_rating": 1100,
        "tags": ["graph", "dfs", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/max-area-of-island/",
        "correct_approach": "DFS from each unvisited land cell. Return size of each island. Track max.",
        "key_concepts": ["DFS returning size", "marking visited in-place", "max across all DFS calls"],
        "common_mistakes": ["not marking visited causing recount", "not returning size from DFS", "using separate visited array when in-place works"]
    },
    {
        "id": "lc-133",
        "platform": "leetcode",
        "title": "Clone Graph",
        "statement": "Given a reference to a node in a connected undirected graph, return a deep copy of the graph.",
        "difficulty_rating": 1200,
        "tags": ["graph", "dfs", "bfs", "hash table"],
        "url": "https://leetcode.com/problems/clone-graph/",
        "correct_approach": "DFS with hash map from original node to cloned node. Clone node before recursing neighbors.",
        "key_concepts": ["hash map old to new node", "clone before recursing", "avoiding infinite loop with visited map"],
        "common_mistakes": ["infinite loop without visited tracking", "not cloning node before adding to map", "shallow copy of neighbors list"]
    },
    {
        "id": "lc-286",
        "platform": "leetcode",
        "title": "Walls and Gates",
        "statement": "Fill each empty room with the distance to its nearest gate. Walls are -1, gates are 0, empty rooms are INF.",
        "difficulty_rating": 1200,
        "tags": ["graph", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/walls-and-gates/",
        "correct_approach": "Multi-source BFS from all gates simultaneously. Distance fills outward level by level.",
        "key_concepts": ["multi-source BFS from all gates", "BFS guarantees shortest distance", "in-place distance update"],
        "common_mistakes": ["BFS from each gate separately causing O(m2n2)", "using DFS which doesn't guarantee shortest", "not initializing all gates in queue first"]
    },
    {
        "id": "lc-417",
        "platform": "leetcode",
        "title": "Pacific Atlantic Water Flow",
        "statement": "Find all cells from which water can flow to both Pacific and Atlantic oceans. Water flows to adjacent cells with equal or lower height.",
        "difficulty_rating": 1500,
        "tags": ["graph", "dfs", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/pacific-atlantic-water-flow/",
        "correct_approach": "Reverse flow: BFS/DFS from ocean borders inward. Find intersection of cells reachable from both.",
        "key_concepts": ["reverse flow from ocean borders", "two separate visited sets", "intersection of reachable sets"],
        "common_mistakes": ["forward flow causing TLE", "not reversing direction for uphill flow", "merging two BFS instead of intersecting"]
    },
    {
        "id": "lc-130",
        "platform": "leetcode",
        "title": "Surrounded Regions",
        "statement": "Given a board with 'X' and 'O', capture all regions of 'O' not connected to the border.",
        "difficulty_rating": 1300,
        "tags": ["graph", "dfs", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/surrounded-regions/",
        "correct_approach": "DFS from all border 'O' cells, mark safe. Convert unmarked 'O' to 'X'. Restore marked.",
        "key_concepts": ["border-connected DFS", "reverse thinking safe cells", "two-pass marking and restoration"],
        "common_mistakes": ["trying to detect surrounded directly which is complex", "not starting from borders", "wrong restoration logic"]
    },

    # ═══════════════════════════════════════════════════════════════
    # GRAPHS - INTERMEDIATE
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-323",
        "platform": "leetcode",
        "title": "Number of Connected Components in Undirected Graph",
        "statement": "Given n nodes and edges, find the number of connected components.",
        "difficulty_rating": 1200,
        "tags": ["graph", "dfs", "union find"],
        "url": "https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/",
        "correct_approach": "DFS counting components or Union Find. Count distinct roots.",
        "key_concepts": ["connected components counting", "union find root counting", "DFS component labeling"],
        "common_mistakes": ["not building adjacency list correctly", "counting nodes instead of components", "not handling isolated nodes"]
    },
    {
        "id": "lc-399",
        "platform": "leetcode",
        "title": "Evaluate Division",
        "statement": "Given equations like a/b = k, answer queries asking for the value of x/y.",
        "difficulty_rating": 1600,
        "tags": ["graph", "dfs", "bfs", "weighted graph"],
        "url": "https://leetcode.com/problems/evaluate-division/",
        "correct_approach": "Build weighted directed graph. Each equation a/b=k adds edge a->b with weight k and b->a with weight 1/k. DFS for each query.",
        "key_concepts": ["weighted graph for division", "bidirectional edges with reciprocal weights", "DFS path product"],
        "common_mistakes": ["not adding reverse edge with reciprocal", "not handling unknown variables", "not resetting visited between queries"]
    },
    {
        "id": "lc-1020",
        "platform": "leetcode",
        "title": "Number of Enclaves",
        "statement": "Given a binary matrix, find the number of land cells from which you cannot walk off the boundary.",
        "difficulty_rating": 1300,
        "tags": ["graph", "dfs", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/number-of-enclaves/",
        "correct_approach": "DFS from all border land cells, mark reachable. Count unmarked land cells.",
        "key_concepts": ["border DFS elimination", "counting enclosed cells", "inverse thinking"],
        "common_mistakes": ["trying to detect enclosed directly", "wrong border cell identification", "counting marked instead of unmarked"]
    },
    {
        "id": "lc-1091",
        "platform": "leetcode",
        "title": "Shortest Path in Binary Matrix",
        "statement": "Given an n x n binary matrix, find the shortest clear path from top-left to bottom-right. Path must go through 0 cells including 8 directions.",
        "difficulty_rating": 1300,
        "tags": ["graph", "bfs", "matrix"],
        "url": "https://leetcode.com/problems/shortest-path-in-binary-matrix/",
        "correct_approach": "BFS from (0,0). 8-directional movement. BFS guarantees shortest path in unweighted graph.",
        "key_concepts": ["BFS for shortest unweighted path", "8-directional movement", "marking visited to avoid revisit"],
        "common_mistakes": ["using DFS which doesn't guarantee shortest", "only 4-directional movement", "not handling start or end being blocked"]
    },
    {
        "id": "lc-547",
        "platform": "leetcode",
        "title": "Number of Provinces",
        "statement": "Given an n x n adjacency matrix where isConnected[i][j]=1 if cities i and j are directly connected, find the number of provinces.",
        "difficulty_rating": 1200,
        "tags": ["graph", "dfs", "union find"],
        "url": "https://leetcode.com/problems/number-of-provinces/",
        "correct_approach": "DFS from each unvisited city, mark all reachable cities. Count DFS calls.",
        "key_concepts": ["adjacency matrix DFS", "province counting", "visited tracking"],
        "common_mistakes": ["confusing adjacency matrix with adjacency list traversal", "double counting provinces", "not handling self-loops in adjacency matrix"]
    },

    # ═══════════════════════════════════════════════════════════════
    # GRAPHS - ADVANCED
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-332",
        "platform": "leetcode",
        "title": "Reconstruct Itinerary",
        "statement": "Given a list of airline tickets, reconstruct the itinerary starting from JFK using all tickets exactly once.",
        "difficulty_rating": 1700,
        "tags": ["graph", "dfs", "Eulerian path"],
        "url": "https://leetcode.com/problems/reconstruct-itinerary/",
        "correct_approach": "Hierholzer's algorithm for Eulerian path. Sort destinations, DFS, append to result on backtrack.",
        "key_concepts": ["Hierholzer Eulerian path", "post-order append for path", "sorted adjacency list for lexical order"],
        "common_mistakes": ["standard DFS which misses dead ends", "not reversing final result", "not sorting destinations for lexical order"]
    },
    {
        "id": "lc-1584",
        "platform": "leetcode",
        "title": "Min Cost to Connect All Points",
        "statement": "Given points on a plane, find minimum cost to connect all points where cost is Manhattan distance.",
        "difficulty_rating": 1500,
        "tags": ["graph", "minimum spanning tree", "Prim", "Kruskal"],
        "url": "https://leetcode.com/problems/min-cost-to-connect-all-points/",
        "correct_approach": "Prim's algorithm with min heap or Kruskal's with union find. MST on complete graph.",
        "key_concepts": ["Prim's algorithm", "minimum spanning tree", "lazy deletion from heap"],
        "common_mistakes": ["generating all edges explicitly O(n2) for Kruskal", "not using heap for Prim making it O(n3)", "adding already visited nodes to MST"]
    },
    {
        "id": "lc-1334",
        "platform": "leetcode",
        "title": "Find the City With the Smallest Number of Neighbors at a Threshold Distance",
        "statement": "Find the city with fewest cities reachable within distance threshold. Return highest-numbered city if tie.",
        "difficulty_rating": 1500,
        "tags": ["graph", "shortest path", "Floyd-Warshall", "Dijkstra"],
        "url": "https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/",
        "correct_approach": "Floyd-Warshall for all-pairs shortest paths. Then count reachable cities per node.",
        "key_concepts": ["Floyd-Warshall all pairs shortest path", "triple nested loop DP", "distance threshold filtering"],
        "common_mistakes": ["running Dijkstra from each node O(n2 logn) when Floyd-Warshall is cleaner", "wrong Floyd-Warshall update order", "not initializing dist[i][i]=0"]
    },
    {
        "id": "lc-785",
        "platform": "leetcode",
        "title": "Is Graph Bipartite?",
        "statement": "Given an undirected graph, determine if it is bipartite (can be 2-colored such that no adjacent nodes share color).",
        "difficulty_rating": 1400,
        "tags": ["graph", "dfs", "bfs", "bipartite"],
        "url": "https://leetcode.com/problems/is-graph-bipartite/",
        "correct_approach": "BFS/DFS coloring. Assign alternating colors. If adjacent nodes have same color, not bipartite.",
        "key_concepts": ["graph 2-coloring", "BFS level alternating color", "detecting odd cycles"],
        "common_mistakes": ["not handling disconnected components", "not starting BFS for all unvisited nodes", "wrong color toggle logic"]
    },
    {
        "id": "lc-269",
        "platform": "leetcode",
        "title": "Alien Dictionary",
        "statement": "Given a sorted list of words in an alien language, derive the order of letters in the alien alphabet.",
        "difficulty_rating": 1800,
        "tags": ["graph", "topological sort", "dfs", "string"],
        "url": "https://leetcode.com/problems/alien-dictionary/",
        "correct_approach": "Build directed graph from adjacent word comparisons. Topological sort. Detect cycles.",
        "key_concepts": ["building graph from word comparisons", "topological sort for ordering", "cycle detection for invalid input"],
        "common_mistakes": ["wrong edge direction", "not handling prefix case as invalid", "missing characters that appear but have no ordering constraint"]
    },

    # ═══════════════════════════════════════════════════════════════
    # DP - BEGINNER
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-198",
        "platform": "leetcode",
        "title": "House Robber",
        "statement": "You cannot rob two adjacent houses. Given array of amounts, find maximum you can rob.",
        "difficulty_rating": 1000,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/house-robber/",
        "correct_approach": "dp[i] = max(dp[i-1], dp[i-2] + nums[i]). Either skip current house or rob it.",
        "key_concepts": ["skip or take DP", "two variable optimization", "no-adjacent constraint"],
        "common_mistakes": ["wrong base cases", "using dp[i-1] when should use dp[i-2] + current", "not optimizing to O(1) space"]
    },
    {
        "id": "lc-213",
        "platform": "leetcode",
        "title": "House Robber II",
        "statement": "Houses are in a circle. You cannot rob two adjacent houses. Find maximum rob amount.",
        "difficulty_rating": 1200,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/house-robber-ii/",
        "correct_approach": "Run House Robber I twice: once excluding first house, once excluding last. Take max.",
        "key_concepts": ["circular constraint as two linear problems", "House Robber I as subroutine", "max of two scenarios"],
        "common_mistakes": ["trying to handle circular case in one pass", "wrong index ranges for two runs", "not understanding why two runs cover all cases"]
    },
    {
        "id": "lc-746",
        "platform": "leetcode",
        "title": "Min Cost Climbing Stairs",
        "statement": "Given cost array where cost[i] is cost of step i, find minimum cost to reach the top. You can climb 1 or 2 steps.",
        "difficulty_rating": 900,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/min-cost-climbing-stairs/",
        "correct_approach": "dp[i] = cost[i] + min(dp[i-1], dp[i-2]). Answer is min(dp[n-1], dp[n-2]).",
        "key_concepts": ["cost DP with two choices", "minimum cost accumulation", "answer at n not n-1"],
        "common_mistakes": ["wrong answer index", "not adding current cost to min of previous two", "off by one in array bounds"]
    },
    {
        "id": "lc-118",
        "platform": "leetcode",
        "title": "Pascal's Triangle",
        "statement": "Given numRows, return the first numRows of Pascal's triangle.",
        "difficulty_rating": 800,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/pascals-triangle/",
        "correct_approach": "Each row starts and ends with 1. Middle elements are sum of two above: triangle[i][j] = triangle[i-1][j-1] + triangle[i-1][j].",
        "key_concepts": ["Pascal recurrence", "row construction from previous row", "boundary elements as 1"],
        "common_mistakes": ["wrong boundary handling", "off by one in inner loop", "not initializing first and last element of each row"]
    },
    {
        "id": "lc-338b",
        "platform": "leetcode",
        "title": "Minimum Path Sum",
        "statement": "Given a grid filled with non-negative numbers, find a path from top-left to bottom-right that minimizes the sum of all numbers along the path.",
        "difficulty_rating": 1100,
        "tags": ["array", "dp", "matrix"],
        "url": "https://leetcode.com/problems/minimum-path-sum/",
        "correct_approach": "dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1]). Initialize first row and column separately.",
        "key_concepts": ["grid path DP", "first row and column initialization", "min of top and left"],
        "common_mistakes": ["wrong base case for edges", "forgetting to add current cell value", "using max instead of min"]
    },

    # ═══════════════════════════════════════════════════════════════
    # DP - INTERMEDIATE
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-647b",
        "platform": "leetcode",
        "title": "Decode Ways",
        "statement": "A message containing letters A-Z is encoded as numbers 1-26. Given a string of digits, return the number of ways to decode it.",
        "difficulty_rating": 1400,
        "tags": ["string", "dp"],
        "url": "https://leetcode.com/problems/decode-ways/",
        "correct_approach": "dp[i] = ways to decode s[:i]. Add dp[i-1] if s[i-1] valid single digit. Add dp[i-2] if s[i-2:i] valid two digits.",
        "key_concepts": ["decode ways recurrence", "single and double digit validity checks", "zero handling"],
        "common_mistakes": ["not handling leading zeros", "wrong two-digit validity range 10-26", "not initializing dp[0]=1 for empty string"]
    },
    {
        "id": "lc-377",
        "platform": "leetcode",
        "title": "Combination Sum IV",
        "statement": "Given an array of distinct integers and a target, return the number of possible combinations that add up to target. Order matters.",
        "difficulty_rating": 1400,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/combination-sum-iv/",
        "correct_approach": "dp[i] = number of ways to reach sum i. For each amount, try all numbers. Order matters so outer loop is target.",
        "key_concepts": ["order-sensitive combination count", "unbounded knapsack with order", "outer loop target inner loop nums"],
        "common_mistakes": ["confusing with combination sum where order doesn't matter", "wrong loop order", "not initializing dp[0]=1"]
    },
    {
        "id": "lc-494",
        "platform": "leetcode",
        "title": "Target Sum",
        "statement": "Given an integer array and target, assign + or - to each number. Find the number of ways to reach target.",
        "difficulty_rating": 1500,
        "tags": ["array", "dp", "backtracking"],
        "url": "https://leetcode.com/problems/target-sum/",
        "correct_approach": "DP with offset. dp[i][sum+offset] = ways. Or reduce to subset sum problem.",
        "key_concepts": ["DP with sum as state", "offset for negative sums", "subset sum reduction"],
        "common_mistakes": ["exponential backtracking without memoization", "not handling negative sum indices", "wrong subset sum reduction math"]
    },
    {
        "id": "lc-518",
        "platform": "leetcode",
        "title": "Coin Change II",
        "statement": "Given coins and an amount, return the number of combinations that make up the amount.",
        "difficulty_rating": 1500,
        "tags": ["array", "dp"],
        "url": "https://leetcode.com/problems/coin-change-ii/",
        "correct_approach": "Unbounded knapsack. Outer loop coins, inner loop amount. dp[j] += dp[j-coin].",
        "key_concepts": ["unbounded knapsack combination count", "outer loop items inner loop capacity", "avoiding duplicate combinations"],
        "common_mistakes": ["reversing loop order causing permutations instead of combinations", "confusing with Coin Change I", "not initializing dp[0]=1"]
    },
    {
        "id": "lc-1048",
        "platform": "leetcode",
        "title": "Longest String Chain",
        "statement": "Given words, find the longest chain where each word is a predecessor of the next (remove one letter to get predecessor).",
        "difficulty_rating": 1500,
        "tags": ["array", "dp", "hash table", "string"],
        "url": "https://leetcode.com/problems/longest-string-chain/",
        "correct_approach": "Sort by length. For each word try removing each character, look up predecessor in dp map.",
        "key_concepts": ["sort by length for DP ordering", "generate all predecessors", "hash map for O(1) lookup"],
        "common_mistakes": ["not sorting by length first", "generating successors instead of predecessors", "wrong predecessor generation loop"]
    },

    # ═══════════════════════════════════════════════════════════════
    # DP - ADVANCED
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-312",
        "platform": "leetcode",
        "title": "Burst Balloons",
        "statement": "Given n balloons with numbers, burst all balloons to maximize coins. Bursting balloon i earns nums[i-1]*nums[i]*nums[i+1].",
        "difficulty_rating": 1800,
        "tags": ["array", "dp", "interval dp"],
        "url": "https://leetcode.com/problems/burst-balloons/",
        "correct_approach": "Interval DP. dp[i][j] = max coins from bursting all balloons between i and j. Think of k as LAST balloon burst in range.",
        "key_concepts": ["interval DP", "last burst not first", "padding with 1s at boundaries"],
        "common_mistakes": ["thinking of k as first burst instead of last", "wrong boundary padding", "wrong interval DP order"]
    },
    {
        "id": "lc-1143b",
        "platform": "leetcode",
        "title": "Stone Game",
        "statement": "Alex and Lee take turns taking stones from either end of a row. Alex goes first. Both play optimally. Does Alex always win?",
        "difficulty_rating": 1400,
        "tags": ["array", "dp", "game theory", "math"],
        "url": "https://leetcode.com/problems/stone-game/",
        "correct_approach": "Math: Alex always wins (return True). Or interval DP: dp[i][j] = max score difference for current player over range [i,j].",
        "key_concepts": ["interval DP for game theory", "score difference DP", "current player advantage"],
        "common_mistakes": ["not understanding it is always True", "wrong DP definition for two players", "not using score difference trick"]
    },
    {
        "id": "lc-115",
        "platform": "leetcode",
        "title": "Distinct Subsequences",
        "statement": "Given strings s and t, return the number of distinct subsequences of s that equal t.",
        "difficulty_rating": 1700,
        "tags": ["string", "dp"],
        "url": "https://leetcode.com/problems/distinct-subsequences/",
        "correct_approach": "2D DP. dp[i][j] = number of ways s[:i] contains t[:j] as subsequence. Two cases: use or skip s[i].",
        "key_concepts": ["subsequence count DP", "use or skip current character", "base case empty t has one match"],
        "common_mistakes": ["wrong transition when characters match", "confusing with LCS", "wrong base case initialization"]
    },
    {
        "id": "lc-10",
        "platform": "leetcode",
        "title": "Regular Expression Matching",
        "statement": "Given string s and pattern p with '.' and '*', implement regex matching.",
        "difficulty_rating": 1900,
        "tags": ["string", "dp", "recursion"],
        "url": "https://leetcode.com/problems/regular-expression-matching/",
        "correct_approach": "2D DP. dp[i][j] = does s[:i] match p[:j]. Handle dot and star cases separately.",
        "key_concepts": ["regex DP", "star matches zero or more", "dot matches any character"],
        "common_mistakes": ["wrong star handling (zero vs one or more)", "not handling p[j]='*' with zero occurrences", "off by one in DP indices"]
    },
    {
        "id": "lc-1770",
        "platform": "leetcode",
        "title": "Maximum Score from Performing Multiplication Operations",
        "statement": "Given nums and multipliers arrays, perform exactly m operations choosing from either end of nums. Maximize score.",
        "difficulty_rating": 1700,
        "tags": ["array", "dp", "memoization"],
        "url": "https://leetcode.com/problems/maximum-score-from-performing-multiplication-operations/",
        "correct_approach": "DP with state (operation index, left pointer). Right pointer derived as left + ops - i.",
        "key_concepts": ["state compression two variable DP", "right pointer derivation", "memoization with tuple key"],
        "common_mistakes": ["using all three variables as state when two suffice", "wrong right index formula", "TLE without memoization"]
    },

    # ═══════════════════════════════════════════════════════════════
    # GRAPH + DP COMBINED
    # ═══════════════════════════════════════════════════════════════

    {
        "id": "lc-329",
        "platform": "leetcode",
        "title": "Longest Increasing Path in a Matrix",
        "statement": "Given an integer matrix, find the length of the longest increasing path. Move in 4 directions.",
        "difficulty_rating": 1700,
        "tags": ["graph", "dp", "dfs", "memoization", "matrix"],
        "url": "https://leetcode.com/problems/longest-increasing-path-in-a-matrix/",
        "correct_approach": "DFS with memoization from each cell. No visited set needed since path is strictly increasing.",
        "key_concepts": ["DFS memoization on grid", "no visited needed for strictly increasing", "cache longest path from each cell"],
        "common_mistakes": ["using visited set causing wrong results", "TLE without memoization", "wrong direction check for increasing"]
    },
    {
        "id": "lc-1293",
        "platform": "leetcode",
        "title": "Shortest Path in a Grid with Obstacles Elimination",
        "statement": "Find shortest path from top-left to bottom-right in binary grid. You can eliminate at most k obstacles.",
        "difficulty_rating": 1800,
        "tags": ["graph", "bfs", "dp", "matrix"],
        "url": "https://leetcode.com/problems/shortest-path-in-a-grid-with-obstacles-elimination/",
        "correct_approach": "BFS with state (row, col, remaining_eliminations). 3D visited array.",
        "key_concepts": ["BFS with extended state", "3D visited array", "state space exploration"],
        "common_mistakes": ["2D visited array missing elimination count", "using DFS instead of BFS", "not pruning states with fewer eliminations remaining"]
    },
    {
        "id": "lc-847",
        "platform": "leetcode",
        "title": "Shortest Path Visiting All Nodes",
        "statement": "Given an undirected graph, find the shortest path length that visits every node.",
        "difficulty_rating": 1800,
        "tags": ["graph", "bfs", "dp", "bitmask"],
        "url": "https://leetcode.com/problems/shortest-path-visiting-all-nodes/",
        "correct_approach": "BFS with bitmask state. State = (node, visited_bitmask). Start from all nodes simultaneously.",
        "key_concepts": ["bitmask DP", "BFS with bitmask state", "multi-source BFS for all starting nodes"],
        "common_mistakes": ["not using bitmask causing exponential state space", "single source BFS missing optimal start", "wrong bitmask operations"]
    },
    {
        "id": "lc-931",
        "platform": "leetcode",
        "title": "Minimum Falling Path Sum",
        "statement": "Given an n x n matrix, find the minimum sum of any falling path. A falling path starts at any element in the first row and goes down choosing from adjacent columns.",
        "difficulty_rating": 1300,
        "tags": ["array", "dp", "matrix"],
        "url": "https://leetcode.com/problems/minimum-falling-path-sum/",
        "correct_approach": "DP in-place. For each cell add minimum of three cells above. Answer is min of last row.",
        "key_concepts": ["falling path DP", "three choices above", "answer in last row"],
        "common_mistakes": ["modifying matrix while reading causing wrong values", "wrong boundary handling for edge columns", "returning wrong answer position"]
    },
    {
        "id": "lc-1696",
        "platform": "leetcode",
        "title": "Jump Game VI",
        "statement": "Given array nums and integer k, start at index 0. Jump at most k steps forward. Maximize sum of visited elements.",
        "difficulty_rating": 1600,
        "tags": ["array", "dp", "sliding window", "monotonic deque", "heap"],
        "url": "https://leetcode.com/problems/jump-game-vi/",
        "correct_approach": "DP with monotonic deque for sliding window maximum. dp[i] = nums[i] + max(dp[i-k..i-1]).",
        "key_concepts": ["DP with sliding window max", "monotonic deque optimization", "O(n) vs O(nk) naive"],
        "common_mistakes": ["naive O(nk) DP without deque", "wrong deque maintenance", "not removing out of window elements from front"]
    },
]


def seed_graphs_dp():
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print(f"Seeding {len(GRAPH_DP_PROBLEMS)} graph and DP problems...")
    success = 0

    for p in GRAPH_DP_PROBLEMS:
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
    print(f"\nDone. {success} graph and DP problems seeded.")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM problems;")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM problems WHERE tags && ARRAY['graph','dfs','bfs','dijkstra','topological sort'];")
    graph_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM problems WHERE tags && ARRAY['dp'];")
    dp_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"\nDatabase summary:")
    print(f"  Total problems : {total}")
    print(f"  Graph problems : {graph_count}")
    print(f"  DP problems    : {dp_count}")


if __name__ == "__main__":
    seed_graphs_dp()
