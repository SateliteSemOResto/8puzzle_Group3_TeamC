😊8 Puzzle A* Solver — Task 1 (Heuristic Search)
This project implements an A* solver for the 8 puzzle with two heuristics (Hamming and Manhattan), a simple CLI to solve single puzzles, and a benchmark to compare heuristics over many random solvable boards.
😊Purpose of Task 1
•	Start from random states, check solvability, and search to the goal using at least two heuristics (Hamming & Manhattan).
•	Measure performance for each heuristic over ~100 random cases: number of expanded nodes (space effort) and runtime; report mean and standard deviation.
•	Provide a short write up with: brief task description, architecture diagram (optional here), module/interface descriptions, design decisions, results discussion, and ideas for improvement.
😊State & Goal
•	State representation: flat 9 tuple of ints 0..8 (0 = blank), row major order.
•	Goal: (1, 2, 3, 4, 5, 6, 7, 8, 0)
1 2 3
4 5 6
7 8 .
Methods (What they do, Inputs → Outputs)
😊hamming(state, goal=GOAL) -> int
Counts misplaced tiles (excluding 0). Returns a non negative integer h.
Input: state (tuple length 9)
Output: h (misplaced tile count)
😊manhattan(state, goal=GOAL) -> int
Sum of Manhattan distances (|dx|+|dy|) for each non blank tile to its goal position.
Input: state
Output: h (distance sum)
😊neighbors(state) -> list[State]
Generates valid successor states by sliding a neighboring tile into the blank (up/down/left/right when legal).
Input: state
Output: list of next states (tuples)
😊is_solvable(state) -> bool
Checks 8 puzzle solvability via inversion count (ignoring 0). Even inversions ⇒ solvable.
Input: state
Output: True/False
😊calculate_costs(g, state, goal=GOAL, heuristic=manhattan) -> (f,g,h)
Computes h = heuristic(state), f = g + h. Utility for A* node scoring.
Input: g (path cost so far), state, optional goal, heuristic
Output: (f, g, h)
😊generate_random_solvable_board(steps=50, seed=None, start_from=GOAL) -> State
Produces a guaranteed solvable board by random walking steps legal moves from the goal (optionally seeded).
Input: scramble steps, optional seed
Output: solvable state
😊run_benchmark(n=100, scramble_steps=50, seed=42, time_limit_seconds=10.0) -> dict
Runs n random solvable test cases for each heuristic. Returns summary stats per heuristic:
•	nodes_mean/std, time_mean_s/std_s, sol_len_mean/std, timeouts.
Input: n, scramble_steps, seed, time_limit_seconds
Output: nested dict of metrics (one entry for hamming, one for manhattan)

😊A* Search (overview)
•	OPEN list: priority queue (min heap) keyed by f = g + h
•	CLOSED set: visited states fully expanded
•	Parent map: child → parent to reconstruct the optimal path
•	Step cost: 1 per move; goal test on pop
😊CLI — Simple User Interface
Run the script and use the menu:
😊8 Puzzle A* Solver (Hamming & Manhattan)
Goal state is:
1 2 3
4 5 6
7 8 .

Menu:
  1) Solve one puzzle
  2) Benchmark heuristics
  3) Quit
>
1) Solve one puzzle
•	Choose random or manual start.
o	Random: enter scramble steps (⏎ for default 40) and optional seed.
o	Manual: type 9 integers (0..8) row wise; 0 is blank. Example: 1 2 3 4 5 6 0 7 8.
•	Pick heuristic: 1 = Hamming, 2 = Manhattan.
•	Output: solution length (moves), nodes expanded, runtime. Optionally print each step.
2) Benchmark heuristics
•	Enter number of cases (e.g., 100), scramble steps (e.g., 50), seed (e.g., 42), and per case time limit.
•	Prints mean/std for nodes expanded and runtime, average solution length, and timeouts for both heuristics.
3) Quit
•	Exit the program.

😊How to Run
python 8_puzzle_a_solver_and_benchmark_python.py
If you use an IDE that doesn’t handle input() well, run it in a proper terminal (VS Code Terminal, macOS Terminal, Windows Terminal/PowerShell).
😊Typical Expectations
•	Manhattan is more informative than Hamming → usually fewer expanded nodes and faster runtime.
•	Solution lengths for random scrambles often average ~18–22 moves; variance is normal.
😊Reporting & Write Up Hints
•	Include a small table comparing Hamming vs Manhattan: nodes mean/std, time mean/std, average solution length, timeouts.
•	State assumptions: uniform step cost, admissible/consistent heuristics.
•	Discuss design choices (state layout, neighbors ordering, RNG seeding, timeouts) and possible improvements (e.g., linear conflict heuristic, bidirectional search, IDA*).
😊Repo Hygiene
•	Keep IDE files out of Git with .gitignore (already included):
o	.idea/, *.iml, __pycache__/, *.py[cod], venv/, .venv/, .vscode/, .DS_Store
😊File List
•	8_puzzle_a_solver_and_benchmark_python.py — full implementation (A*, heuristics, CLI, benchmarking)
•	.gitignore — ignore IDE/OS/Python cache files
•	README.md — this file
