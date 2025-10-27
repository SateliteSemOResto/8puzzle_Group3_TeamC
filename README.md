This project implements an Informed Search algorithm to solve the classic 8-Puzzle problem starting from a random initial state. The core objective is to analyse the performance and complexity of the A* search algorithm using two different admissible heuristic functions: the Hamming Distance (h1​) and the Manhattan Distance (h2​). The implementation was carried out in Python.
 
Software Architecture and Interfaces
The search process involves several modular components, structured for clarity and efficiency
The diagram should illustrate the flow from board generation, solvability check, cost calculation, and the main A* search loop utilizing the open and closed lists.

flowchart TD

---------- Single Solve Pipeline ----------
	A[Random State Generation\n(generate_random_solvable_board)] --> B{isSolvable()?}
	B -- No --> X[Report: Unsolvable / Regenerate]
	B -- Yes --> C[A* Search Loop]
	subgraph C1[A* Search Loop]
  	C --> C2[calculateCosts()\n g (moves)\n h (heuristic)\n f = g + h]
  	C --> C3[Priority Queue (Open Set)\nmin-heap by f, tie-break]
  	C --> C4[Closed Set (Visited)]
  	C2 --> C3
  	C3 -->|pop best f| C5[Expand State\nneighbors()]
  	C5 -->|update g,f,parents| C3
  	C5 -->|mark visited| C4
  	C5 -->|goal found| D[Solution Path / Metrics]
	end
	D --> E[Solution Path Reconstruction\n(reconstruct_path)]
	D --> F[Metrics Collection\nnodes_expanded, runtime_ms, solution_length]
 
flowchart LR

---------- Benchmark Orchestration ----------
	G[runBenchmark()\n(run_experiment)] --> H[Loop for N Trials]
	H --> I[Random State Generation\n(seed, scramble_moves)]
	I --> J{isSolvable()?}
	J -- No --> I
	J -- Yes --> K[A* with Hamming] --> L[Record Metrics]
	J -- Yes --> M[A* with Manhattan] --> L
	L --> N[Summarize & Report\n(mean, std)\n(print_table)]
Module Descriptions and Interfaces
The following is a list of key submodules implemented, detailing their purpose and interface requirements
<img width="1376" height="1119" alt="image" src="https://github.com/user-attachments/assets/eea1d8e4-5287-4678-b42f-0856fb44a527" />
<img width="1375" height="446" alt="image" src="https://github.com/user-attachments/assets/593c7ea7-a6fe-4436-8a22-bcdc145ccc87" />

Design Decisions:
 Separation of concerns (clean layers)
UI layer: menus, prompts, pretty printing only (no search logic).
Experiment layer: run_experiment → summarize → print_table orchestrates the benchmark and reporting.
Search engine: a_star, calculate_costs implement A* and nothing else.
Heuristics: hamming, manhattan are pure, testable functions.
Domain/utilities: neighbors, is_solvable, generate_random_solvable_board handle puzzle mechanics.
Data model: State (immutable tuple), and Node(f,h,g,state) for the priority queue.
This keeps responsibilities small and testable, and mirrors the screenshots/flows.

A* correctness & performance choices
Optimality: A* with admissible h (Hamming/Manhattan) on unit costs ⇒ optimal path.
Heap (min-priority queue): always expand the lowest f=g+h in O(log N), not O(N).
best_g map: prune worse paths to the same state, reducing expansions.
Tie-break: ordering by (f, h) favors smaller h on ties, often guiding search better.
Puzzle-specific decisions
Solvability check: is_solvable (inversion parity) prevents wasted search on impossible boards.
State immutability: State as a tuple makes hashing fast & reliable for closed/open sets.
Neighbors: minimal, deterministic blank moves; easy to test.


Random start generation: random walk from GOAL guarantees solvable without repeated shuffles.
 Benchmark design (fair, reproducible, report-ready)
Fairness: each trial uses the same start state for both heuristics.


Reproducibility: master seed feeds per-trial seeds, so results can be replicated exactly.


Metrics:


nodes_expanded = search effort/memory proxy,


runtime_ms = wall-clock performance,


solution_length = optimality check.


Summaries: summarize reports mean/std per heuristic; print_table formats a clear table for the write-up.

Algorithm Selection
The A* Search algorithm was chosen because, when coupled with an admissible heuristic h(s), it is complete, guaranteed to find a solution if one exists and optimal, guaranteed to find the solution with the lowest cost
 
Heuristic Choice and Admissibility: Two heuristics were implemented for comparison-
1. Hamming Distance (h_1): This is admissible because the total number of moves required to solve the puzzle is always at least the number of misplaced tiles, meaning h1​ never overestimates the true cost.
2. Manhattan Distance (h_2): This is admissible because every tile must be moved at least the number of spots separating it from its goal position. This also never overestimates the true cost
 
Data Structure Selection: The choice of data structures was crucial for mitigating the exponential complexity of the search:
• Open List (States to Explore): A Priority Queue was used. This efficiently manages the frontier by ensuring that the node with the minimum total cost f(s) is always selected next for expansion, which is the defining characteristic of A* search.
• Closed List (Explored States): A Set was used. Sets allow for extremely fast lookups (O(1) complexity) to check whether a state has already been fully explored, preventing redundant searches and cycles
Quantitative Results and Comparison: The performance comparison was conducted over 100 random, solvable start states for each heuristic. We measured Memory Effort (expanded nodes) and Run Time (computation time)
<img width="1388" height="571" alt="image" src="https://github.com/user-attachments/assets/d62a86cf-85f6-4a1b-a931-67166eaad541" />


Analysis of Results: The benchmark clearly demonstrates the superior performance of the Manhattan Distance (h_2) heuristic compared to the Hamming Distance (h1​).
1. Memory Effort (Expanded Nodes): h2​ expanded a mean of 1,491.47 nodes, which is nearly ten times fewer nodes than h1​ (14,761.33 nodes). This confirms that h2​ performs significantly better in terms of memory usage and search tree pruning.
2. Run Time: The reduction in expanded nodes translates directly into faster computation time, with h2​ requiring only 7.53 ms on average, compared to 72.69 ms for h1​.
3. Optimality: Since both heuristics are admissible, the resulting mean solution length (21.36) is identical for both, confirming that the A* algorithm finds the optimal path regardless of the admissible heuristic used.
Theoretical Justification: This performance disparity is explained by the concept of dominance. h2​ is considered the better heuristic because it dominates h1​, meaning that from any node n, h2​(n)>h1​(n). Because h2​ provides a higher (more accurate) estimate of the true cost to the goal while still being admissible, it leads to better pruning of the search tree, thereby reducing the time and space complexity in practice.
<img width="1314" height="380" alt="image" src="https://github.com/user-attachments/assets/54e099b6-207d-4a27-a05d-d05def0fb2ac" />



Personal Experience:
Motivation- I built this to study A* on the 8-puzzle and compare admissible heuristics (Hamming vs. Manhattan) with reproducible benchmarks.
Key learnings
- A* + min-heap frontier ⇒ efficient expansion by lowest \(f=g+h\); admissible \(h\) guarantees optimal paths.
- Random walk from goal produces solvable starts; inversion parity validates manual inputs.
- Manhattan is typically stronger than Hamming in practice (fewer expansions, faster).
Design choices
- Clear layering: UI → experiment → A* engine → heuristics → utilities.
- Immutable `State` (tuple), `best_g` pruning, and tie-break on `(f, h)`.
- Metrics per run: `nodes_expanded`, `runtime_ms`, `solution_length`.
Challenges & fixes
- Simplified code into small, commented functions matching the assignment API.
- Ensured fairness by solving the **same start** with both heuristics each trial.
- Managed heavy instances via better heuristics and pruning.

 <img width="1395" height="440" alt="image" src="https://github.com/user-attachments/assets/286a9371-e573-4e07-897d-c9d31d34e5bd" />
The complexity for calculating h(s) is O(1) because the problem size (9 tiles) is fixed. The overall complexity of A* search is determined by the effective branching factor (b^*), which is significantly reduced by the higher-quality h_2 heuristic, as evidenced by the decrease in expanded nodes.


