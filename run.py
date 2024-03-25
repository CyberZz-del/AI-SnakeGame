from greedy_solver import GreedySolver
from hamilton_solver import HamiltonSolver


dic_solver={
    "greedy":"GreedySolver",
    "hamilton":"HamiltonSolver"
}

#choose GreedySolver or HamiltonSolver to check different algorithms
game=HamiltonSolver()
game.run()