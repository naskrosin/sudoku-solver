#! python3
# -*- coding: utf8 -*-

''' Exception Classes for Cell and Grid objects. '''

class CellError(Exception):
    def __init__(self, row, column, message):
        Exception.__init__(self, message)
        self.row, self.col = row, column

class CellSetError(CellError):
    def __init__(self, row, column, number, message):
        CellError.__init__(self, row, column, message)
        self.num = number

class CellGetError(CellError):
    def __init(self, row, column, message):
        CellError.__init__(self, row, column, message)

class GridBuildError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
