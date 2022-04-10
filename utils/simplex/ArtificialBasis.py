from fractions import Fraction
from accessify import private

from utils.simplex.SimplexTable import SimplexTable


class ArtificialBasis(SimplexTable):

    def __init__(self, matrix_a: list, matrix_b: list, matrix_c: list, signs: list, is_maximize: bool, basis='x'):
        self.is_maximize = is_maximize
        self.is_first_stage = True
        table = []
        for row in matrix_a:
            table.append(row.copy())
        for i in range(len(table)):
            table[i].append(matrix_b[i])
        table.append(matrix_c.copy() + [0])
        for i in range(len(table[0])):
            table[len(table) - 1][i] = -table[len(table) - 1][i]
        pos = len(matrix_a)
        artificial_basis_indexes = []
        for i in range(len(signs)):
            if signs[i] == '>=':
                for j in range(len(table)):
                    if i == j:
                        table[j].insert(pos, Fraction(-1))
                    else:
                        table[j].insert(pos, Fraction(0))
                pos += 1
                for j in range(len(table)):
                    if i == j:
                        table[j].insert(pos, Fraction(1))
                        artificial_basis_indexes.append(pos)
                    else:
                        table[j].insert(pos, Fraction(0))
                pos += 1
            elif signs[i] == '==':
                for j in range(len(table)):
                    if i == j:
                        table[j].insert(pos, Fraction(1))
                        artificial_basis_indexes.append(pos)
                    else:
                        table[j].insert(pos, Fraction(0))
                pos += 1
            elif signs[i] == '<=':
                for j in range(len(table)):
                    if i == j:
                        table[j].insert(pos, Fraction(1))
                    else:
                        table[j].insert(pos, Fraction(0))
                pos += 1
            else:
                raise Exception("Invalid sign")
        table.append(ArtificialBasis.add_artificial_function(table, signs, artificial_basis_indexes).copy())
        rows = len(table)
        columns = len(table[0])
        columns_caption = []
        for i in range(columns - 1):
            columns_caption.append(basis + str(i + 1))
        columns_caption.append('b')
        rows_caption = []
        for i in range(rows - 2):
            for j in range(columns - 2, 0, -1):
                if table[i][j] == 1:
                    rows_caption.append(columns_caption[j])
                    break
        rows_caption.append('Z')
        rows_caption.append('G')
        super().__init__(table, rows, columns, rows_caption, columns_caption)

    @staticmethod
    def add_artificial_function(table: list, signs: list, indexes: list):
        artificial_function = [0] * len(table[0])
        for i in range(len(table) - 1):
            for j in range(len(table[i])):
                if (signs[i] == '>=' or signs[i] == '==') and indexes.count(j) == 0:
                    artificial_function[j] -= table[i][j]
        return artificial_function

    def drop_artificial_function(self):
        if not self.is_first_stage:
            raise Exception('Artificial function already dropped')
        self.table.pop()
        self.rows -= 1
        self.is_first_stage = False

    @private
    def find_column(self):
        value = Fraction()
        index = -1
        for i in range(self.columns - 1):
            c = self.table[self.rows - 1][i]
            find_maximum = self.is_first_stage or self.is_maximize
            if c < value and find_maximum or c > value and not find_maximum:
                value = c
                index = i
        return index

    @private
    def find_row(self, column: int):
        value = Fraction(-1)
        index = -1
        for i in range(self.rows - 1 - int(self.is_first_stage)):
            a = self.table[i][column]
            b = self.table[i][self.columns - 1]
            if (b >= 0 and a > 0 or b < 0 and a < 0) and (b / a < value or value < 0):
                value = b / a
                index = i
        return index

    def can_be_iterated(self):
        find_maximum = self.is_first_stage or self.is_maximize
        for i in range(self.columns - 1):
            c = self.table[self.rows - 1][i]
            if find_maximum and c < 0 or not find_maximum and c > 0:
                return True
        return False

    @private
    def resize(self, row: int, column: int):
        pop_index = self.columns_caption.index(self.rows_caption[row])
        self.columns_caption.pop(pop_index)
        for table_row in self.table:
            table_row.pop(pop_index)
        if pop_index < column:
            column -= 1
        self.columns -= 1
        return column

    def iterate(self):
        column = self.find_column()
        row = self.find_row(column)
        element = 'Element: {} ({}, {})'.format(str(self.table[row][column]), row + 1, column + 1)
        if self.is_first_stage:
            column = self.resize(row, column)
        self.recalculate(row, column)
        return element

    def get_data(self):
        return self.table, self.rows_caption, self.columns_caption, self.is_maximize
