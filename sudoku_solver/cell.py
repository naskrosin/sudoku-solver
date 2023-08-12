#! python3
# -*- coding: utf8 -*-
from sudoku_solver.exceptions import CellSetError, CellGetError, GridBuildError

class Cell:
    def __init__(self, num=0, row=0, col=0, mute=False):
        self.__num = num
        self.__row = row
        self.__col = col
        self.__mute = mute
        self.__pool = []

    def __str__(self):
        return f'_{self.__num}_, ({self.__row}, {self.__col})'

    def __lt__(self, other):
        lessrow = self.__row < other.loc().get('row')
        lesscol = (self.__row == other.loc().get('row') and self.__col < other.loc().get('col'))
        return lessrow or lesscol

    def getn(self) -> int:
        return self.__num

    def setn(self, number):
        '''
        set number to Cell object if its not already occupied with games start;
        raise CellSetError otherwise.
        '''
        if self.usrn():
            self.__num = number
            self.__pool.clear()
        else:
            raise CellSetError(self.__row, self.__col, self.__num, "Cell already occupied")

    def box(self) -> int: 
        ''' return the number of which 'subgrid' the cell exists. '''
        row, column = self.loc().values()
        for r in range(1, 10, 3):
            if r <= row < r + 3:
                sqrs = range(r, r+3)

        if 9 / column >= 3:
            return sqrs[0]
        if 9 / column < 1.5:
            return sqrs[2]
        return sqrs[1]

    def setpool(self, pool:list) -> bool:
        self.__pool = pool
        return True

    def poolrmv(self, numbers:list):
        try:
            for num in filter(lambda n: n in self.__pool, numbers):
                self.__pool.remove(num)
        except TypeError:
            print("Cell.poolrmv requires 'list' as argument.")
            raise

    def getpool(self) -> list:
        return self.__pool[:]

    def loc(self, points=False) -> dict:
        if points:
            return (self.__row, self.__col)
        return {'row': self.__row, 'col': self.__col}

    def cp(self, other):
        self.__num = other.getn()
        self.__row = other.loc().get('row')
        self.__col = other.loc().get('col')
        self.__mute = other.usrn()
        self.__pool = other.getpool()

    def usrn(self) -> bool:
        return self.__mute
