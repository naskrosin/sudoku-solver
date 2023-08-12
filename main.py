#! python3
# -*- coding: utf8 -*-

import random
from sudoku_solver.grid import Grid
from sudoku_solver.puzzles import hard#easy#, medium, hard


#game = Grid() # creating an empty Grid object
#puzzle = random.choice(easy) # taking a random puzzle from easy list
#
#game.build(puzzle) # building the Grid object with puzzle numbers
#game.draw() # print current status of the Grid
#
#game.solve() # solve and print the Grid puzzle

for p in hard:
    g = Grid()
    g.build(p)
    g.solve()
