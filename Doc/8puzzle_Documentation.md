# 8 Puzzle Documentation

### Team

| Name 						               |
|---------------------------|
| Junu Rahman                	 |
| Helena Mouro		            |
| 				           |
| 					          |

### Short task description


### Software architecture diagram
![UML Component Diagram](Diagram.png)

### Short descriptions of modules and interfaces
| Module 						                | Description           | Functions                                                                                    |
|------------------------------|------------------------------|----------------------------------------------------------------------------------------------|
| Heuristics                	 | | hamming(state)<br/>manhattan(state)                                                          |
| Mechanics		               | | neighbors(state)<br/>is_solvable(state)                                                      |
| A* Search				                         || a_star(...)<br/>calculateCosts(...)<br/>reconstruct_path(...)                                |
| Random generator					                        || generate_random_solvable_board(...)                                                          |
| UI & helpers					                        || format_state(state)<br/>ask_int(...)<br/> parse_state_from_input(...)<br/>choose_heuristic(...) |
| UI actions				                        || ui_solve_once()<br/>ui_benchmark()|
| Experiment/Benchmark				                        || run_experiment(...)<br/>summarize(...)<br/>print_table(...)|


### Design decisions
-why truple choosen to save the puzzles

### Discussion and conclusion



