#! python3
# -*- coding: utf8 -*-

''' a program for solving sudoku boards. '''

import math
import sys
from sudoku_solver.cell import Cell
from sudoku_solver.exceptions import CellSetError, CellGetError, GridBuildError


class Grid:
    def __init__(self):
        self.grid = []
        
    def __str__(self):
        pass

    def build(self, puzzle:str) -> None:
        ''' 
        build a grid object out of listed rows (2d array);
        and set up pool of numbers for each cell.
        '''
        arrange = []
        for row in puzzle.split():
            arrange.append([int(cel) for cel in row])
        try:
            if len(arrange) != 9:
                raise GridBuildError('Invalid Row amount in Grid')

            for r, rws in enumerate(arrange):
                if len(rws) != 9:
                    raise GridBuildError('Invalid Column amount in Grid')
                self.grid.extend([
                    Cell(num, r+1, c+1) if num != 0 else Cell(num, r+1, c+1, mute=True) \
                    for c, num in enumerate(rws)
                    ])
        except GridBuildError as griderr:
            sys.exit(griderr)
        self.set_pools()

    def draw(self, same:list=[]):
        ''' print the grid to the console. '''
        rows = ['' for i in range(len(self.grid)//9)]
        for r in range(0, len(self.grid), 3):
            line = []
            for cell in self.grid[r:r+3]:
                if cell.getn() == 0:
                    line.append(' '*3)
                elif len(list(filter(lambda m: cell.loc() == m.loc() , same))) > 0:
                    line.append('{aro}{cell}{aro}'.format(aro='~', cell=str(cell.getn())))
                else:
                    line.append(' '+ str(cell.getn()) +' ')

            line = '[{seg}]'.format(seg=']['.join(line))
            lastr = '\n' if (r+3) % 9 == 0 and r != 0 else '||'
            rows[r//9] += line + lastr

        for s in range(0, len(rows), 3):
            print(( '-' * len(rows[0]) + '\n' ).join(rows[s:s+3]), end="")
            if s+3 < len(rows):
                print('|'*len(rows[0])+'\n', end="")
        print()

    def getall(self) -> list:
        ''' return Grid cells. '''
        return self.grid

    def cleargrid(self):
        ''' clear the Grid list. '''
        self.grid.clear()

    def copy(self, other):
        ''' copy other Grid cells to self. '''
        self.cleargrid()
        for cell in other.getall():
            new = Cell()
            new.cp(cell)
            self.grid.append(new)

    def get(self, loc:tuple) -> Cell:
        ''' get the cell object requested at row, column. '''
        try:
            for cell in self.grid:
                if cell.loc().get('row') == loc[0] and cell.loc().get('col') == loc[1]:
                    return cell
            raise CellGetError(loc[0], loc[1], "Can't find requested Cell:")
        except CellGetError as cellerr:
            print(cellerr, f'({cellerr.row}, {cellerr.col})')

    def empties(self):
        ''' get a list of all empty cells. '''
        return list(filter(lambda e: e.getn() == 0, self.grid))

    def row(self, cell:Cell, empty=False, withme=True) -> list:
        ''' return all cells in Row of passed Cell object;
            empty: to get only empty cells within row
            withme: to include the Cell object passed on to the method
            '''
        row = []
        for c in filter(lambda d: (d is not cell) or withme, self.grid):
            if c.loc().get('row') == cell.loc().get('row'):
                row.append(c)

        return list(filter(lambda r: (r.getn() == 0) or not empty, row))

    def column(self, cell:Cell, empty=False, withme=True) -> list:
        ''' return all cells in Column of passed Cell object;
            empty: to get only empty cells within column
            withme: to include the Cell object passed on to the method
            '''
        col = []
        for c in filter(lambda d: (d is not cell) or withme, self.grid):
            if c.loc().get('col') == cell.loc().get('col'):
                col.append(c)

        return list(filter(lambda r: (r.getn() == 0) or not empty, col))
    
    def circle(self, cell:Cell, empty=False, withme=True) -> list:
        ''' return all cells in Subgrid of passed Cell object;
            empty: to get only empty cells within box
            withme: to include the Cell object passed on to the method
            '''
        rend, cend = map(lambda v: math.ceil(v / 3) * 3, [cell.loc().get('row'), cell.loc().get('col')])
        rstart, cstart = [i - 3 for i in [rend, cend]]

        box = []
               
        for e in filter(
                lambda k: ((k is not cell) or withme) and ((k.getn() == 0) or not empty),
                self.grid
                ):

            if (rstart < e.loc().get('row') <= rend) and (cstart < e.loc().get('col') <= cend):
                box.append(e)

        return box

    def union(self, cell:Cell) -> list:
        ''' return a list of unavailable selection of numbers according to the cell location. '''
        uni = []
        nines = map(
                lambda g: (c.getn() for c in g),
                [self.row(cell), self.column(cell), self.circle(cell)]
            )
        
        for nine in nines:
            uni.extend(filter(lambda n: n not in uni , nine))

        return uni

    def nines(self, cell:Cell, empty=False, withme=True) -> iter:
        ''' return generator from areas (row, column and box), which the Cell placed in. '''
        for nine in [
                self.row(cell, empty, withme),
                self.column(cell, empty, withme),
                self.circle(cell, empty, withme)
                ]:
            yield nine

    def preimeter(self, cell:Cell, empty=False, withme=True) -> list:
        ''' create a list over iteration of the Cells row, column and box;
            and return the list with all the cells in these areas.
            '''
        cells = []
        for nine in self.nines(cell, empty, withme):
            cells.extend(filter(lambda c: c not in cells, nine))
        return cells
    

    def absent(self, cell:Cell) -> list:
        ''' get a list of available selections according to row, column and box of The Cell. '''
        absents = []
        for i in range(1, 10):
            if i not in self.union(cell):
                absents.append(i)
        return absents


    def set_pools(self):
        ''' set choices of numbers(pool) in empty cells. '''
        for z in self.empties():
            z.setpool(self.absent(z))
    
    def cellnum(self, cell:Cell, number):
        ''' set cell number and update others pools in preimeter. '''
        cell.setn(number)
        for others in self.preimeter(cell, empty=True, withme=False):
            others.poolrmv([number])


    def has_twin(self, cell:Cell, preimeter, ln=2):
        ''' find out if there is a neighbor subgrid cell that has same pool numbers of "ln" '''
        pool = cell.getpool()
        if len(pool) == ln:
            for j in filter(lambda a: a is not cell, preimeter):
                if pool == j.getpool():
                    return True
        return False

    def single_choice_check(self, cell:Cell) -> list:
        ''' return pool if there is only only one available number in the Cells pool. '''
        if len(cell.getpool()) == 1:
            return cell.getpool()[0]
        return False

    def not_others_check(self, cell:Cell) -> list:
        ''' checks the pool of The Cell with other cells in preimeter,
         and if there is a number only placeable in the Cell,
         return it in a list of 1 length.
         '''
        for preimeter in [
                self.row(cell, empty=True, withme=False),
                self.column(cell, empty=True, withme=False),
                self.circle(cell, empty=True, withme=False)
                ]:

            select = cell.getpool()
            for a in preimeter:
                select = list(filter(lambda r: r not in a.getpool(), select))

            if len(select) == 1:
                return select[0]
        return False
            

    def straight_clean(self, cell:Cell):
        ''' remove numbers from pool that other cells in row, column and box are occupied with '''
        cell.poolrmv(list(filter(lambda r: r in cell.getpool(), self.union(cell))))

    def box_clean(self, cell:Cell):
        ''' If there is a choice of number which is only placeable in The Cell
            location (looking from its Row/Column precpective), and placeable 
            only in any other cells in its box which have the same Row/Column
            of the Cell, Then remove that number from other cells in the box,
            other than the ones in the same Row/Column.
            '''
        for gen in [self.row(cell, empty=True), self.column(cell, empty=True)]:
            # bind generator to 'line' because after first iteration, generator becomes empty
            line = list(gen)
            for num in cell.getpool():
                if list(filter(lambda o: o.box() != cell.box() and num in o.getpool(), line)) == []:
                    for z in filter(lambda y: y not in line and num in y.getpool(), self.circle(cell, empty=True)): 
                        z.poolrmv([num])

    def twin_clean(self, cell:Cell):
        ''' if found any twins in preimeter, remove the numbers from other cells in that preimeter '''
        for nine in self.nines(cell, empty=True):
            if self.has_twin(cell, nine):
                for others in filter(lambda f: f.getpool() != cell.getpool() , nine):
                    others.poolrmv(cell.getpool())
    
    def check(self):
        ''' iterate through empty cells and return a list with found numbers '''
        found = []
        self.clean()
        for empty in self.empties():
            checks = list(filter(
                    lambda ch: ch is not False,
                    [self.single_choice_check(empty), self.not_others_check(empty)]
                    ))
            if len(checks) > 0:
                found.append((empty, checks[0]))
        return found

    def clean(self):
        ''' clean all empty cells in Grid '''
        for cleaner in [self.straight_clean, self.box_clean, self.twin_clean]:
            for empty in self.empties():
                cleaner(empty)

    def check_and_set(self):
        ''' check and fill cells with right number from check;
            iterate as long as all empty cells are filled or the
            loop is exhausted.
            '''
        while len(self.check()) > 0:
            for cell, number in self.check():
                self.cellnum(cell, number)
        if len(self.empties()) == 0:
            return True
        return False

    def findall(self):
        ''' first case checks empty cells with 'check_and_set' method;
            if returns True, then return all cells in Grid object.
            second case checks if there is a wrong number in all filled
            cells, by searching empty cells to find an empty pool;
            in this case method returns False.
            after that function iterates through empty cells of Grid and
            uses recursion between an available selection only placeable
            in 2 spots.
            '''

        if self.check_and_set():
            return self.getall()

        # if there is an empty cell that there cannot be any valid choices
        # for that cell (pool is empty), return False and exit current recursion.
        if len(list(filter(lambda x: len(x.getpool()) == 0, self.empties()))) != 0:
            return False

        for cell in self.empties():
            for nine in self.nines(cell, empty=True, withme=False):
                pools = []
                for p in map(lambda g: g.getpool(), nine):
                    pools.extend(p)
                for number in cell.getpool():
                    if pools.count(number) == 1:
                        # use a new copy Grid to call recursive method on
                        new = Grid()
                        new.copy(self)
                        new.cellnum(new.get(cell.loc(points=True)), number)

                        # start of recursion
                        fill = new.findall()
                        if fill is not False: # only during which 'check_and_set' returns True,
                            return fill       # this condition executes

    def solve(self):
        ''' call 'findall' method and fill current Grid with right numbers. '''
        same = []
        fill = self.findall()
        try:
            for cell in fill:
                try:
                    self.cellnum(self.get(cell.loc(points=True)), cell.getn())
                except CellSetError:
                    same.append(cell)
        except TypeError:
            print('Sorry, something went wrong there')
            return
        self.draw(same)

def main():
    puzzle = [
            [6, 9, 0,  4, 0, 5,  0, 7, 0],
            [0, 0, 4,  9, 0, 0,  0, 0, 1],
            [8, 0, 5,  7, 6, 0,  4, 2, 9],

            [0, 4, 6,  1, 0, 0,  0, 3, 2],
            [0, 0, 0,  0, 9, 0,  0, 0, 5],
            [5, 0, 3,  2, 8, 4,  0, 0, 6],

            [3, 5, 1,  0, 0, 0,  0, 0, 0],
            [0, 0, 0,  8, 3, 0,  2, 5, 0],
            [2, 8, 0,  0, 0, 0,  6, 0, 0]
        ]

    game = Grid()
    game.build(puzzle)
    game.draw()

if __name__ == '__main__':
    main()
