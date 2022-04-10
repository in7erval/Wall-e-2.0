import re
from abc import ABC, abstractmethod
from fractions import Fraction
from accessify import protected


class SimplexTable(ABC):
    def __init__(self, table: list, rows: int, columns: int, rows_caption: list, columns_caption: list):
        self.table = table
        self.rows = rows
        self.columns = columns
        self.rows_caption = rows_caption
        self.columns_caption = columns_caption

    @protected
    def recalculate(self, row: int, column: int):
        self.rows_caption[row] = self.columns_caption[column]
        new_table = []
        for table_row in self.table:
            new_table.append(table_row.copy())
        for i in range(len(self.table)):
            for j in range(len(self.table[i])):
                if i == row and j == column:
                    new_table[i][j] = Fraction(1)
                elif i != row and j == column:
                    new_table[i][j] = Fraction(0)
                elif i == row and j != column:
                    new_table[i][j] = Fraction(self.table[i][j] / self.table[row][column]).limit_denominator(
                        max_denominator=1000)
                else:
                    a11 = self.table[i][j]
                    a12 = self.table[row][j]
                    a21 = self.table[i][column]
                    a22 = self.table[row][column]
                    new_table[i][j] = Fraction(a11 - a12 * a21 / a22).limit_denominator(max_denominator=1000)
        self.table = new_table

    @abstractmethod
    def can_be_iterated(self):
        pass

    @abstractmethod
    def iterate(self):
        pass

    def print(self):
        for caption in ([''] + self.columns_caption):
            print('{:>6}'.format(caption), end=' ')
        print()
        for i in range(self.rows):
            print('{:>6}'.format(self.rows_caption[i]), end=' ')
            for element in self.table[i]:
                print('{:>6}'.format(str(element)), end=' ')
            print()

    def get_table_to_print(self):
        table = []
        row_in_table = []
        for caption in ([''] + self.columns_caption):
            row_in_table.append(caption)
        table.append(row_in_table.copy())
        for i in range(self.rows):
            row_in_table.clear()
            row_in_table.append(self.rows_caption[i])
            for element in self.table[i]:
                row_in_table.append(str(element))
            table.append(row_in_table.copy())
        return table

    def get_function_answer(self):
        return self.table[self.rows - 1][self.columns - 1]

    @staticmethod
    def get_basis_index(basis: str):
        return int(re.search('(\d+)', basis).group(0))

    def get_vector_answer(self):
        size = SimplexTable.get_basis_index(self.columns_caption[self.columns - 2])
        answer = [Fraction()] * size
        for i in range(self.rows - 1):
            index = SimplexTable.get_basis_index(self.rows_caption[i])
            answer[index - 1] = self.table[i][self.columns - 1]
        return answer
