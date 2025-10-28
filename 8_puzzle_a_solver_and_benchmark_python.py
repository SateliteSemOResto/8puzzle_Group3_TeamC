#!/usr/bin/env python3

from heapq import heappush, heappop
from typing import Callable, Dict, Iterable, List, Optional, Tuple
import math, random, time, itertools
from statistics import mean, stdev

# ----------------------------- Types & constants -----------------------------

State = Tuple[int,...]                 #tuple of ints
GOAL: State = (1, 2, 3, 4, 5, 6, 7, 8, 0) #0 is the blank

def goal_pos(v: int):
    i = GOAL.index(v)
    row= i//3
    col=i%3
    return (row, col)

# ----------------------------- Heuristics -----------------------------------

def hamming(state: State, goal: State = GOAL) -> int:
    """Number of misplaced tiles (excluding blank)."""
    return sum(1 for i, v in enumerate(state) if v != 0 and v != goal[i])

def manhattan(state: State) -> int:
    """Sum of |dr|+|dc| from each tile to its goal position (excluding blank)."""
    d = 0
    for i, v in enumerate(state):
        if v == 0:
            continue
        r, c = divmod(i, 3)
        gr, gc = goal_pos(v)
        d += abs(r - gr) + abs(c - gc)
    return d

# ----------------------------- Mechanics ------------------------------------
def neighbors(state: State):
    """All valid states by sliding the blank tile around."""
    zeroPos = state.index(0)        #getting the blank tiles index
    zRow, zCol = divmod(zeroPos, 3)     #getting blank tiles 3x3 index
    possibles: List[State] = []
    for moveRow, moveCol in [(-1, 0), (1, 0), (0, -1), (0, 1)]: #for every movement
        newR, newC = zRow + moveRow, zCol + moveCol
        if 0 <= newR < 3 and 0 <= newC < 3:     #if the movement is possible
            newZeroPos = newR * 3 + newC        #change blank tiles position
            nState = list(state)                      #get a new stable, tuples are impermutable
            nState[zeroPos], nState[newZeroPos] = nState[newZeroPos], nState[zeroPos]
            possibles.append(tuple(nState))            #add new state after movement to list of possible states
    return possibles
    """After getting the 3x3 index of the blank tile (value "0"), it is created a lists of the new possible states. 
    Every blank tile movement is checked for its plausibility, and the ones possible are added to a list of states. """

def is_solvable(state: State) -> bool:
    """Solvable if inversion count is even (for 3×3)."""
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):  # for every tile on the board
        for j in range(i + 1, len(arr)):  # for every tile +1
            if arr[i] > arr[j]:  # checks if the previous tile is bigger than the next
                inv += 1  # if so, an inversion was found
    return inv % 2 == 0
"""After creating a new list with all tiles except the blank, it goes through all the tiles to check
     where there are inversions. After summing all inversion, it is divided by two. Returning true (solvable)
      if the remainder is zero, or false (not solvable) if the remainder is one."""

# ----------------------------- A* Search ------------------------------------

def _calc_f(g: int, state: State, heuristic: Callable[[State], int]) -> int:
    """Calculate total cost f(n) = g(n) + h(n).""" 
    return g + heuristic(state)

def reconstruct_path(parents: Dict[State, Optional[State]], goal_state: State) -> List[State]:
    """Reconstruct path from goal to start using parent pointers."""
    path = [goal_state]
    while parents[path[-1]] is not None:
        path.append(parents[path[-1]])
    path.reverse()
    return path

def a_star(start: State,
           goal: State = GOAL,
           heuristic: Callable[[State], int] = manhattan,
           time_limit_seconds: Optional[float] = None) -> Tuple[List[State], int, float]:
    """ Returns: (solution_path, number_of_nodes_expanded, time_taken_in_seconds)
    Empty path -> not solved (unsolvable or timed out)."""

    #Step 1: Check if puzzle is already solved or unsolvable
    if start == goal:
        return [start], 0, 0.0
    if not is_solvable(start):
        return [], 0, 0.0

    #Step 2: Initialize variables
    start_time = time.perf_counter()
    open_list: List[Tuple[int, int, State]] = [] #Priority queue: (f_score, tie_breaker, state)
    g_scores: Dict[State, int] = {start: 0} #Cost from start to each state
    parents: Dict[State, Optional[State]] = {start: None} #Path tracking
    visited: set[State] = set() #Explored states
    tie_breaker = itertools.count() #Ensures consistent orderning
    nodes_expanded = 0

    #Step3: Add start state to queue
    f_start = _calc_f(0, start, heuristic)
    heappush(open_list, (f_start, next(tie_breaker), start))

    #Step 4: Main loop
    while open_list:
        #Optional timeout check
        if time_limit_seconds and (time.perf_counter() - start_time) > time_limit_seconds:
            return [], nodes_expanded, time.perf_counter() - start_time
        
        #Get state with lowest f(n)
        _,_, current = heappop(open_list)
        if current in visited:
            continue
        visited.add(current)
        nodes_expanded +=1

        #Goal check
        if current == goal:
            path = reconstruct_path(parents, current)
            return path, nodes_expanded, time.perf_counter() - start_time
        
        #Step5: Explore neighbors
        current_g = g_scores[current]
        for neighbor in neighbors(current):
            if neighbor in visited:
                continue

            tentative_g = current_g +1 #Each move costs 1
            if tentative_g < g_scores.get(neighbor, math.inf):
                g_scores[neighbor] = tentative_g
                parents[neighbor] = current
                f_score = _calc_f(tentative_g, neighbor, heuristic)
                heappush(open_list, (f_score, next(tie_breaker), neighbor))
        
    #No solution found
    return[], nodes_expanded, time.perf_counter() - start_time


# ----------------------------- Random generator -----------------------------

def generateRandomSolvableBoard(steps: int, startState: State = GOAL) :
    """Random walk from GOAL state == guaranteed solvable state."""

    rand = random.Random()  #initializes randomizer
    s = startState
    prev: State = None

    for i in range(steps):      #for however many steps to diverge from goal state
        nextStates = neighbors(s)       #get possible boards
        if prev is not None and len(nextStates) > 1:
            nextStates = [x for x in nextStates if x != prev] #creates new list with only new moves
        if nextStates is None:      #if there aren't any, return last board
            assert is_solvable(s)
            return s
        prev = s
        s= rand.choice(nextStates)
    assert is_solvable(s)
    return s
    """Creates a new board from backward stepping from the solved board. For however many steps, it checks board neighbors
     (possible moves) and picks a random one. After making sure the steps that preceeded that board can't be picked."""
# ----------------------------- Pretty-print & UI helpers --------------------
# This function makes the 3x3 puzzle.
# Example:
# (1,2,3,4,5,6,7,8,0) becomes:
# 1 2 3
# 4 5 6
# 7 8 .

def format_state(state: State) -> str:
    rows = []
    for r in range(3): # Loop through each of the 3 rows
        row = state[3*r:3*r+3]
        rows.append(" ".join("." if x == 0 else str(x) for x in row)) # Replace 0 with a dot "." and join numbers with spaces
    return "\n".join(rows) # Combine all rows with line breaks

# This function safely asks the user to type a whole number.
# It repeats until the input is valid (a number, not a letter).
# It also supports a default value and a minimum allowed value.

def ask_int(prompt, default=None, min_val=None):
    while True:
        if default is not None:
            user_input = input(f"{prompt} [default {default}]: ")
        else:
            user_input = input(f"{prompt}: ")
        if user_input == "" and default is not None:  # If user pressed Enter with no input, use the default
            return default
        try:
            number = int(user_input) # try to convert text to a number
        except:
            print("Please type a whole number.")
            continue # go back and ask again

        if min_val is not None and number < min_val:  # Check if the number is at least the minimum allowed
            print(f"The number must be at least {min_val}.")
            continue  # too small, ask again
        return number


# This function lets the user enter their own puzzle manually.
# It checks that they enter 9 numbers (0–8) with no duplicates.

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

# This function asks which heuristic the user wants:
# 1 = Hamming, 2 = Manhattan
def choose_heuristic() -> Callable[[State], int]:
    while True:
        print("Choose heuristic:\n  1) Hamming (misplaced tiles)\n  2) Manhattan (sum of distances)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return lambda s: hamming(s, GOAL)
        elif choice == "2":
            return lambda s: manhattan(s)
        else:
            print("Invalid choice. Please Try again.")

# ----------------------------- UI actions -----------------------------------

def ui_solve_once():
    print("\n=== Solve a single puzzle ===")

    # Ask user: random or manual puzzle
    choice = input("Use random or manual state? (r/m): ").strip().lower()
    if choice == "":
        choice = "r"  # default is random

    # Get the starting puzzle
    if choice == "m":
        # User enters puzzle manually
        start = parse_state_from_input()
    else:
        # Random puzzle: ask for scramble steps and optional seed
        steps = ask_int("How many Random scramble steps?", default=40, min_val=1)
        start = generateRandomSolvableBoard(steps=steps)

    # Show starting puzzle board
    print("\nStart state:\n" + format_state(start))
    print(f"Solvable: {is_solvable(start)}")
    # Ask which heuristic to use (Hamming or Manhattan)
    hfun = choose_heuristic()

    # Solve the puzzle using A* algorithm
    print("Solving, please wait...")
    path, expanded, elapsed = a_star(start, GOAL, hfun)

    # If no solution found (unsolvable or timeout)
    if not path:
        print("No solution (unsolvable or timed out).");
        return

    # Show final result
    print(f"\nSolved in {len(path)-1} moves; expanded {expanded} nodes; {elapsed*1000:.2f} ms.")
    # Ask if user wants to see every step of the solution
    show_steps = input("Show solution steps? [y/N] ").strip().lower()
    if show_steps == "y" :
        for i, st in enumerate(path):
            print(f"\nStep {i}:\n{format_state(st)}")

# ----------------------------- Experiment / Benchmark -----------------------
# This function runs many random puzzles and compares the two heuristics.
def run_experiment(num_trials: int = 100, seed: int = 123, scramble_moves: int = 50) -> List[dict]:

    random_gen = random.Random(seed)
    rows: List[dict] = []

    # List of heuristics to test
    heuristics: List[Tuple[str, Callable[[State], int]]] = [
        ("Hamming", lambda s: hamming(s, GOAL)),
        ("Manhattan", lambda s: manhattan(s)),
    ]
    # Run the given number of trials
    for t in range(1, num_trials + 1):
        # Make a random solvable puzzle
        start = generateRandomSolvableBoard(scramble_moves)
        # Solve the puzzle using both heuristics
        for name, heuristic_function in heuristics:
            path, expanded, elapsed = a_star(start, GOAL, heuristic_function)
            rows.append({
                "trial": t,
                "heuristic": name,
                "nodes_expanded": expanded,
                "runtime_ms": elapsed * 1000.0, # convert seconds to ms
                "solution_length": len(path) - 1 if path else 0,
            })
    return rows

# This function calculates averages (mean) and spread (standard deviation)
# for each heuristic's results.

def summarize(rows: List[dict]) -> List[dict]:
    by_h = {"Hamming": [], "Manhattan": []}
    for r in rows:
        by_h[r["heuristic"]].append(r)
    out = []
    for name, items in by_h.items():
        # Helper function to get a list of one column
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
        # Sort so Hamming appears first
    out.sort(key=lambda d: d["heuristic"])
    return out

# This function prints the results nicely as a table
def print_table(rows: List[dict]) -> None:
    header = ("heuristic | trials | mean_nodes_expanded | std_nodes_expanded | "
           "mean_runtime_ms | std_runtime_ms | mean_solution_length | std_solution_length")
    print(header); print("-"*len(header))
    for r in rows:
        print(f"{r['heuristic']:<10} | {r['trials']:<6} | "
              f"{r['mean_nodes_expanded']:<19} | {r['std_nodes_expanded']:<18} | "
              f"{r['mean_runtime_ms']:<15} | {r['std_runtime_ms']:<14} | "
              f"{r['mean_solution_length']:<19} | {r['std_solution_length']}")

# This function interacts with the user and runs the benchmark.
def ui_benchmark():
    print("\n=== Benchmark (random cases) ===")
    # Ask for number of trials (how many random puzzles)
    try: t = int(input("Trials [100]: ") or 100)
    except ValueError: t = 100
    # Ask for number of random moves to scramble each puzzle
    try: scramble_steps = int(input("Scramble steps per case [50]: ") or 50)
    except ValueError: scramble_steps = 50
    # Ask for random seed safely (no crash on letters)
    while True:
        seed_in = input("Seed (int) or blank: ").strip()
        if seed_in == "":
            seed = 123
            break
        try:
            seed = int(seed_in)
            break
        except ValueError:
            print("Please type a whole number or leave it blank.")
            # loop again until user enters valid number
        # --------------------------------
     # Run experiment and print the results
    rows = run_experiment(num_trials=t, seed=seed, scramble_moves=scramble_steps)
    print("\n8-PUZZLE A* — Hamming vs. Manhattan")
    print(f"(trials={t}, scramble={scramble_steps}, seed={seed})\n")
    print_table(summarize(rows))

# ----------------------------- Main menu ------------------------------------

# This is the main function — it shows the menu and lets the user
# choose what they want to do: solve one puzzle or run benchmarks, or quit.
def main():
    # Print the program title
    print("8-Puzzle A* Solver (Hamming & Manhattan)")
    # Show the goal (final) puzzle state so the user knows what we are solving toward
    print("Goal state:\n" + format_state(GOAL))
    while True:
        # Show menu options
        print("\nMenu:\n  1) Solve one puzzle\n  2) Benchmark heuristics\n  3) Quit")
        # Ask the user for their choice
        c = input("> ").strip()
        # Option 1 → user wants to solve a puzzle
        if c == "1":
            ui_solve_once()
        # Option 2 → user wants to run benchmark comparison
        elif c == "2":
            ui_benchmark()
        # Option 3 → user wants to exit the program
        elif c == "3":
            print("Bye!")
            break
        # Any other input → invalid choice
        else:
            print("Invalid choice. Try 1, 2 or 3.")

if __name__ == "__main__":
    main()
