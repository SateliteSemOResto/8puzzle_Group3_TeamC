#!/usr/bin/env python3
"""
8-Puzzle A* — all-in-one script
- A* search with Hamming & Manhattan heuristics
- Random solvable generator (random walk from goal)
- Interactive UI: Solve one puzzle / Benchmark heuristics
- Experiment runner: prints summary table (mean & std)

Python: 3.9+ (standard library only)
Author: Junu Rahman (single-file consolidation)
"""

from heapq import heappush, heappop
from typing import Callable, Dict, Iterable, List, Optional, Tuple
import math, random, time, itertools
from statistics import mean, stdev

# ----------------------------- Types & constants -----------------------------

State = Tuple[int, ...]                 # 9-length tuple; 0 is the blank
GOAL: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_POS = {v: (i // 3, i % 3) for i, v in enumerate(GOAL)}     #retrieves the goal position of a value

# ----------------------------- Heuristics -----------------------------------

def hamming(state: State, goal: State = GOAL) -> int:
    """Number of misplaced tiles (excluding blank)."""
    return sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i])
    """Iterates through the current state tuple, adding both the index (i, from 0 to 8) and the value (v, the tile number at that position).
    It sums to the count everything both conditions are true (meaning the tile is not the blank + is misplaced)"""

def manhattan(state: State, goal_pos: Dict[int, Tuple[int, int]] = GOAL_POS) -> int:
    """Sum of |dr|+|dc| from each tile to its goal position (excluding blank)."""
    d = 0
    for i, v in enumerate(state):
        if v == 0:                  #avoiding blank tile
            continue
        r, c = divmod(i, 3)
        gr, gc = goal_pos[v]
        d += abs(r - gr) + abs(c - gc)
    return d
    """Given the index and value of a tile, r (row) and c (column) equal the index in a 3x3 grid, gr and gc equal the goal 3x3 grid index of the value."""

# ----------------------------- Mechanics ------------------------------------

def neighbors(state: State) -> List[State]:
    """All valid states by sliding a tile into the blank."""
    i0 = state.index(0)
    r, c = divmod(i0, 3)
    out: List[State] = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            j = nr * 3 + nc
            s = list(state)
            s[i0], s[j] = s[j], s[i0]
            out.append(tuple(s))
    return out
    """After getting the 3x3 index of the tile with value "0", it is created a list of the state, since a truple is impermutable. 
    Then every slide is checked for it's plausibility, and the ones possible are added to a list of states. """

def is_solvable(state: State) -> bool:
    """Solvable iff inversion count is even (for 3×3)."""
    arr = [x for x in state if x != 0]      #all tiles except blank
    inv = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv % 2 == 0
    """After creating a new list with all tiles except the blank, it goes through all the tiles to check where there are inversions.
     After summing all inversion, it is divided by two. Returning true (solvable) if the remainder is zero, or false (not solvable) if the remainder is one."""

# ----------------------------- A* Search ------------------------------------

def calculateCosts(g: int, state: State, heuristic: Callable[[State], int]) -> int:
    return g + heuristic(state)

def reconstruct_path(parents: Dict[State, Optional[State]], end: State) -> List[State]:
    path = [end]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    path.reverse()
    return path

def a_star(start: State,
           goal: State = GOAL,
           heuristic: Callable[[State], int] = manhattan,
           time_limit_seconds: Optional[float] = None) -> Tuple[List[State], int, float]:
    """
    Returns: (solution_path, nodes_expanded, elapsed_seconds)
    Empty path -> not solved (unsolvable or timed out).
    """
    if start == goal:
        return [start], 0, 0.0
    if not is_solvable(start):
        return [], 0, 0.0

    t0 = time.perf_counter()
    counter = itertools.count()                         # tie-breaker
    open_heap: List[Tuple[int, int, State]] = []       # (f, tie, state)
    g_score: Dict[State, int] = {start: 0}
    parents: Dict[State, Optional[State]] = {start: None}
    closed: set[State] = set()

    heappush(open_heap, (calculateCosts(0, start, heuristic), next(counter), start))
    expanded = 0

    while open_heap:
        if time_limit_seconds is not None and (time.perf_counter() - t0) > time_limit_seconds:
            return [], expanded, time.perf_counter() - t0

        f, _, current = heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        expanded += 1

        if current == goal:
            return reconstruct_path(parents, current), expanded, time.perf_counter() - t0

        gc = g_score[current]
        for nb in neighbors(current):
            if nb in closed:
                continue
            ng = gc + 1
            if ng < g_score.get(nb, math.inf):
                g_score[nb] = ng
                parents[nb] = current
                heappush(open_heap, (calculateCosts(ng, nb, heuristic), next(counter), nb))

    return [], expanded, time.perf_counter() - t0  # should not occur for solvable states

# ----------------------------- Random generator -----------------------------

def generate_random_solvable_board(steps: int = 50,
                                   seed: Optional[int] = None,
                                   start_from: State = GOAL) -> State:
    """Random walk from GOAL -> guaranteed solvable state."""
    rng = random.Random(seed)
    s = start_from
    prev: Optional[State] = None
    for _ in range(steps):
        succ = neighbors(s)
        if prev is not None and len(succ) > 1:
            succ = [x for x in succ if x != prev] or succ
        s, prev = rng.choice(succ), s
    assert is_solvable(s)
    return s

# ----------------------------- UI & helpers --------------------

def format_state(state: State) -> str:
    rows = []
    for r in range(3):
        row = state[3*r:3*r+3]
        rows.append(" ".join("." if x == 0 else str(x) for x in row))
    return "\n".join(rows)

def ask_int(prompt: str, default: Optional[int] = None, min_val: Optional[int] = None) -> int:
    while True:
        raw = input(f"{prompt} " + (f"[default {default}] " if default is not None else "")).strip()
        if not raw and default is not None:
            return default
        try:
            val = int(raw)
        except ValueError:
            print("Please enter an integer."); continue
        if min_val is not None and val < min_val:
            print(f"Must be >= {min_val}"); continue
        return val

def parse_state_from_input() -> State:
    print("Enter 9 numbers (0..8) row-wise; 0 is blank. Example: 1 2 3 4 5 6 7 8 0")
    while True:
        parts = input("> ").strip().replace(",", " ").split()
        if len(parts) != 9:
            print("Please enter exactly 9 integers."); continue
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            print("Only integers 0..8 are allowed."); continue
        if sorted(nums) != list(range(9)):
            print("Numbers must be a permutation of 0..8."); continue
        return tuple(nums)  # type: ignore

def choose_heuristic() -> Callable[[State], int]:
    while True:
        print("Choose heuristic:\n  1) Hamming (misplaced tiles)\n  2) Manhattan (sum of distances)")
        c = input("> ").strip()
        if c == "1": return lambda s: hamming(s, GOAL)
        if c == "2": return lambda s: manhattan(s)
        print("Invalid choice. Try again.")

# ----------------------------- UI actions -----------------------------------

def ui_solve_once():
    print("\n=== Solve a single puzzle ===")
    src = (input("Use (r)andom or (m)anual state? [r/m] ").strip().lower() or "r")
    if src.startswith("m"):
        start = parse_state_from_input()
    else:
        steps = ask_int("Random scramble steps?", default=40, min_val=1)
        seed_q = input("Provide seed? [y/N] ").strip().lower() == "y"
        seed = ask_int("Seed (int)?") if seed_q else None
        start = generate_random_solvable_board(steps=steps, seed=seed)

    print("\nStart state:\n" + format_state(start))
    print(f"Solvable: {is_solvable(start)}")
    hfun = choose_heuristic()
    print("Solving...")
    path, expanded, elapsed = a_star(start, GOAL, hfun)
    if not path:
        print("No solution (unsolvable or timed out)."); return

    print(f"\nSolved in {len(path)-1} moves; expanded {expanded} nodes; {elapsed*1000:.2f} ms.")
    if input("Show solution steps? [y/N] ").strip().lower() == "y":
        for i, st in enumerate(path):
            print(f"\nStep {i}:\n{format_state(st)}")

# ----------------------------- Experiment / Benchmark -----------------------

def run_experiment(num_trials: int = 100,
                   seed: int = 123,
                   scramble_moves: int = 50) -> List[dict]:
    rng = random.Random(seed)
    rows: List[dict] = []
    heuristics: List[Tuple[str, Callable[[State], int]]] = [
        ("Hamming", lambda s: hamming(s, GOAL)),
        ("Manhattan", lambda s: manhattan(s)),
    ]
    for t in range(1, num_trials + 1):
        start = generate_random_solvable_board(scramble_moves, seed=rng.randint(0, 10**9))
        for name, h in heuristics:
            path, expanded, elapsed = a_star(start, GOAL, h)
            rows.append({
                "trial": t,
                "heuristic": name,
                "nodes_expanded": expanded,
                "runtime_ms": elapsed * 1000.0,
                "solution_length": len(path) - 1 if path else 0,
            })
    return rows

def summarize(rows: List[dict]) -> List[dict]:
    by_h = {"Hamming": [], "Manhattan": []}
    for r in rows:
        by_h[r["heuristic"]].append(r)
    out = []
    for name, items in by_h.items():
        def col(k): return [x[k] for x in items]
        out.append({
            "heuristic": name,
            "trials": len(items),
            "mean_nodes_expanded": round(mean(col("nodes_expanded")), 2),
            "std_nodes_expanded":  round(stdev(col("nodes_expanded")), 3),
            "mean_runtime_ms":     round(mean(col("runtime_ms")), 4),
            "std_runtime_ms":      round(stdev(col("runtime_ms")), 4),
            "mean_solution_length":round(mean(col("solution_length")), 2),
            "std_solution_length": round(stdev(col("solution_length")), 4),
        })
    out.sort(key=lambda d: d["heuristic"])
    return out

def print_table(rows: List[dict]) -> None:
    hdr = ("heuristic | trials | mean_nodes_expanded | std_nodes_expanded | "
           "mean_runtime_ms | std_runtime_ms | mean_solution_length | std_solution_length")
    print(hdr); print("-"*len(hdr))
    for r in rows:
        print(f"{r['heuristic']:<10} | {r['trials']:<6} | "
              f"{r['mean_nodes_expanded']:<19} | {r['std_nodes_expanded']:<18} | "
              f"{r['mean_runtime_ms']:<15} | {r['std_runtime_ms']:<14} | "
              f"{r['mean_solution_length']:<19} | {r['std_solution_length']}")

def ui_benchmark():
    print("\n=== Benchmark (random cases) ===")
    try: t = int(input("Trials [100]: ") or 100)
    except ValueError: t = 100
    try: sc = int(input("Scramble steps per case [50]: ") or 50)
    except ValueError: sc = 50
    seed_in = input("Seed (int) or blank: ").strip()
    seed = int(seed_in) if seed_in else 123
    rows = run_experiment(num_trials=t, seed=seed, scramble_moves=sc)
    print("\n8-PUZZLE A* — Hamming vs. Manhattan")
    print(f"(trials={t}, scramble={sc}, seed={seed})\n")
    print_table(summarize(rows))

# ----------------------------- Main menu ------------------------------------

def main():
    print("8-Puzzle A* Solver (Hamming & Manhattan)")
    print("Goal state:\n" + format_state(GOAL))
    while True:
        print("\nMenu:\n  1) Solve one puzzle\n  2) Benchmark heuristics\n  3) Quit")
        c = input("> ").strip()
        if c == "1":
            ui_solve_once()
        elif c == "2":
            ui_benchmark()
        elif c == "3":
            print("Bye!")
            break
        else:
            print("Invalid choice. Try 1, 2 or 3.")

if __name__ == "__main__":
    main()
