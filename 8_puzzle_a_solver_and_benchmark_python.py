3#!/usr/bin/env python3
"""
8-Puzzle A* Solver with Hamming and Manhattan heuristics
- Priority queue (heapq) for OPEN list
- set for CLOSED list
- parent mapping for path reconstruction
- Functions required by the assignment:
    hamming(), manhattan(), neighbors(), is_solvable(), calculate_costs(),
    generate_random_solvable_board(), run_benchmark()
- Simple command-line user interface

State representation:
- A state is a flat tuple of 9 integers (0..8), where 0 is the blank.
  Index layout (row-major):
      0 1 2
      3 4 5
      6 7 8

Author: (your name)
"""
from __future__ import annotations
import heapq
import itertools
import math
import random
import statistics
import time
from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

State = Tuple[int, ...]  # 9-length tuple, 0..8 where 0 = blank

GOAL: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# -----------------------------
# Heuristics
# -----------------------------

def hamming(state: State, goal: State = GOAL) -> int:
    """Count misplaced tiles (excluding blank 0).

    Args:
        state: current 8-puzzle state (tuple of length 9)
        goal: goal state (default: GOAL)
    Returns:
        Number of tiles out of place (0..8)
    """
    return sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i])


def manhattan(state: State, goal: State = GOAL) -> int:
    """Sum of |dx|+|dy| distances of each tile to its goal position (excluding blank).

    Args:
        state: current 8-puzzle state
        goal: goal state
    Returns:
        Manhattan distance heuristic value (non-negative int)
    """
    # Precompute goal positions
    pos_goal = {v: (i // 3, i % 3) for i, v in enumerate(goal)}
    dist = 0
    for i, v in enumerate(state):
        if v == 0:
            continue
        r, c = divmod(i, 3)
        rg, cg = pos_goal[v]
        dist += abs(r - rg) + abs(c - cg)
    return dist

# -----------------------------
# Core 8-puzzle mechanics
# -----------------------------

def neighbors(state: State) -> List[State]:
    """Generate all valid neighboring states by sliding a tile into the blank.

    Args:
        state: current state
    Returns:
        A list of successor states (each a 9-tuple)
    """
    idx0 = state.index(0)
    r, c = divmod(idx0, 3)
    moves = []
    # Up, Down, Left, Right deltas
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            j = nr * 3 + nc
            new_state = list(state)
            new_state[idx0], new_state[j] = new_state[j], new_state[idx0]
            moves.append(tuple(new_state))
    return moves


def is_solvable(state: State) -> bool:
    """Return True iff the 8-puzzle state is solvable.

    For 3x3 puzzle, solvability is equivalent to even number of inversions
    (counting pairs of tiles (a,b) with a<b but position(a) > position(b)),
    ignoring the blank.
    """
    arr = [x for x in state if x != 0]
    inversions = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inversions += 1
    return inversions % 2 == 0


def calculate_costs(
    g: int,
    state: State,
    goal: State = GOAL,
    heuristic: Callable[[State, State], int] = manhattan,
) -> Tuple[int, int, int]:
    """Compute f, g, h for a node.

    Args:
        g: path cost so far (depth)
        state: the state to evaluate
        goal: goal state
        heuristic: heuristic function
    Returns:
        (f, g, h) where f = g + h
    """
    h = heuristic(state, goal)
    return g + h, g, h

# -----------------------------
# A* search with priority queue, closed set, and parent mapping
# -----------------------------

def reconstruct_path(parents: Dict[State, Optional[State]], end: State) -> List[State]:
    path = [end]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    path.reverse()
    return path


def a_star(
    start: State,
    goal: State = GOAL,
    heuristic: Callable[[State, State], int] = manhattan,
    time_limit_seconds: Optional[float] = None,
) -> Tuple[List[State], int, float]:
    """A* search for the 8-puzzle.

    Args:
        start: initial state
        goal: goal state
        heuristic: h-function (admissible recommended)
        time_limit_seconds: optional cutoff
    Returns:
        (solution_path, nodes_expanded, elapsed_seconds)
        If no solution found within time limit, returns ([], expanded, elapsed)
    """
    if start == goal:
        return [start], 0, 0.0
    if not is_solvable(start):
        return [], 0, 0.0

    t0 = time.perf_counter()

    counter = itertools.count()  # tie-breaker
    open_heap: List[Tuple[int, int, State]] = []  # (f, tie, state)
    g_score: Dict[State, int] = defaultdict(lambda: math.inf)
    parents: Dict[State, Optional[State]] = {start: None}
    closed: set[State] = set()

    g_score[start] = 0
    f0, _, _ = calculate_costs(0, start, goal, heuristic)
    heapq.heappush(open_heap, (f0, next(counter), start))

    nodes_expanded = 0

    while open_heap:
        if time_limit_seconds is not None and (time.perf_counter() - t0) > time_limit_seconds:
            return [], nodes_expanded, time.perf_counter() - t0

        f, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(parents, current), nodes_expanded, time.perf_counter() - t0

        gc = g_score[current]
        for nb in neighbors(current):
            if nb in closed:
                continue
            tentative_g = gc + 1  # each move cost = 1
            if tentative_g < g_score[nb]:
                g_score[nb] = tentative_g
                parents[nb] = current
                fnb, _, _ = calculate_costs(tentative_g, nb, goal, heuristic)
                heapq.heappush(open_heap, (fnb, next(counter), nb))

    # No solution (shouldn't happen for solvable 8-puzzle)
    return [], nodes_expanded, time.perf_counter() - t0

# -----------------------------
# Random generator
# -----------------------------

def generate_random_solvable_board(
    steps: int = 50,
    seed: Optional[int] = None,
    start_from: State = GOAL,
) -> State:
    """Generate a random solvable state via random walk from GOAL.

    Args:
        steps: number of random legal moves to apply
        seed: optional RNG seed for reproducibility
        start_from: state to start scrambling from (default GOAL)
    Returns:
        A solvable 8-puzzle state
    """
    rng = random.Random(seed)
    s = start_from
    prev: Optional[State] = None
    for _ in range(steps):
        succ = neighbors(s)
        # Avoid immediately undoing the last move for a better shuffle
        if prev is not None and len(succ) > 1:
            succ = [x for x in succ if x != prev] or succ
        s, prev = rng.choice(succ), s
    assert is_solvable(s)
    return s

# -----------------------------
# Benchmarking
# -----------------------------

def run_benchmark(
    n: int = 100,
    scramble_steps: int = 50,
    seed: Optional[int] = 42,
    time_limit_seconds: Optional[float] = 10.0,
) -> Dict[str, Dict[str, float]]:
    """Run N random test cases for both heuristics and report mean/std.

    Metrics: nodes_expanded, runtime_seconds, solution_length

    Returns a nested dict {heuristic_name: {metric: value, ...}}
    """
    rng = random.Random(seed)
    test_states = [generate_random_solvable_board(scramble_steps, rng.randint(0, 10**9)) for _ in range(n)]

    results = {}
    for name, hfun in [("hamming", hamming), ("manhattan", manhattan)]:
        nodes_list: List[int] = []
        time_list: List[float] = []
        length_list: List[int] = []

        for s in test_states:
            path, expanded, elapsed = a_star(s, GOAL, hfun, time_limit_seconds)
            nodes_list.append(expanded)
            time_list.append(elapsed)
            length_list.append(len(path) - 1 if path else math.nan)

        # Filter NaN lengths (in case of timeouts)
        length_vals = [x for x in length_list if not math.isnan(x)]
        results[name] = {
            "nodes_mean": statistics.mean(nodes_list),
            "nodes_std": statistics.pstdev(nodes_list),
            "time_mean_s": statistics.mean(time_list),
            "time_std_s": statistics.pstdev(time_list),
            "sol_len_mean": statistics.mean(length_vals) if length_vals else float("nan"),
            "sol_len_std": statistics.pstdev(length_vals) if length_vals else float("nan"),
            "timeouts": sum(1 for p in length_list if math.isnan(p)),
        }

    return results

# -----------------------------
# Pretty printing & UI helpers
# -----------------------------

def format_state(state: State) -> str:
    rows = []
    for r in range(3):
        row = state[3*r:3*r+3]
        rows.append(" ".join("." if x == 0 else str(x) for x in row))
    return "\n".join(rows)


def ask_int(prompt: str, default: Optional[int] = None, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    while True:
        raw = input(f"{prompt} " + (f"[default {default}] " if default is not None else "")).strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
        except ValueError:
            print("Please enter an integer.")
            continue
        if min_val is not None and val < min_val:
            print(f"Must be >= {min_val}")
            continue
        if max_val is not None and val > max_val:
            print(f"Must be <= {max_val}")
            continue
        return val


def parse_state_from_input() -> State:
    print("Enter 9 numbers (0..8) row-wise, where 0 is the blank. Example: 1 2 3 4 5 6 7 8 0")
    while True:
        raw = input("> ").strip().replace(",", " ")
        parts = [p for p in raw.split() if p]
        if len(parts) != 9:
            print("Please enter exactly 9 integers.")
            continue
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            print("Only integers 0..8 are allowed.")
            continue
        if sorted(nums) != list(range(9)):
            print("Numbers must be a permutation of 0..8.")
            continue
        return tuple(nums)  # type: ignore


def choose_heuristic() -> Callable[[State, State], int]:
    while True:
        print("Choose heuristic:\n  1) Hamming (misplaced tiles)\n  2) Manhattan (sum of distances)")
        choice = input("> ").strip()
        if choice == "1":
            return hamming
        if choice == "2":
            return manhattan
        print("Invalid choice. Try again.")


def ui_solve_once():
    print("\n=== Solve a single puzzle ===")
    source = input("Use (r)andom or (m)anual state? [r/m] ").strip().lower() or "r"
    if source.startswith("m"):
        start = parse_state_from_input()
    else:
        steps = ask_int("Random scramble steps?", default=40, min_val=1)
        seed = ask_int("Seed (int)?", default=None) if input("Provide seed? [y/N] ").strip().lower() == "y" else None
        start = generate_random_solvable_board(steps=steps, seed=seed)

    print("Start state:")
    print(format_state(start))
    print(f"Solvable: {is_solvable(start)}")

    hfun = choose_heuristic()
    print("Solving...")
    path, expanded, elapsed = a_star(start, GOAL, hfun)
    if not path:
        print("No solution found (possibly timed out).")
        return

    print(f"Solved in {len(path)-1} moves, expanded {expanded} nodes in {elapsed:.4f} s")
    if input("Show solution steps? [y/N] ").strip().lower() == "y":
        for i, st in enumerate(path):
            print(f"\nStep {i}:\n{format_state(st)}")


def ui_benchmark():
    print("\n=== Benchmark (random cases) ===")
    n = ask_int("How many cases?", default=100, min_val=1)
    steps = ask_int("Scramble steps per case?", default=50, min_val=1)
    seed = ask_int("Seed (int)?", default=42)
    limit = ask_int("Per-case time limit in seconds?", default=10, min_val=1)

    print("Running... this may take a while.")
    stats = run_benchmark(n=n, scramble_steps=steps, seed=seed, time_limit_seconds=float(limit))

    def show(name: str):
        s = stats[name]
        print(
            f"\n{name.upper()}\n  nodes: mean={s['nodes_mean']:.1f}, std={s['nodes_std']:.1f}\n"
            f"  time[s]: mean={s['time_mean_s']:.4f}, std={s['time_std_s']:.4f}\n"
            f"  sol_len: mean={s['sol_len_mean']:.2f}, std={s['sol_len_std']:.2f}\n"
            f"  timeouts: {s['timeouts']} of {n}"
        )

    show("hamming")
    show("manhattan")


def main():
    print("8-Puzzle A* Solver (Hamming & Manhattan)")
    print("Goal state is:\n" + format_state(GOAL))

    while True:
        print("\nMenu:\n  1) Solve one puzzle\n  2) Benchmark heuristics\n  3) Quit")
        choice = input("> ").strip()
        if choice == "1":
            ui_solve_once()
        elif choice == "2":
            ui_benchmark()
        elif choice == "3":
            print("Bye!")
            break
        else:
            print("Invalid choice. Try 1, 2 or 3.")


if __name__ == "__main__":
    main()
