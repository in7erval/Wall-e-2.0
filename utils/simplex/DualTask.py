from utils.simplex.ArtificialBasis import ArtificialBasis


class DualTask:
    def __init__(self, matrix_a: list, filename: str, matrix_b: list, matrix_c: list, is_maximize: bool,
                 is_to_console=True):
        matrix_a_t = []
        self.filename = filename
        for i in range(len(matrix_a[0])):
            row_a = []
            for j in range(len(matrix_a)):
                row_a.append(matrix_a[j][i])
            matrix_a_t.append(row_a.copy())
            row_a.clear()
        matrix_b_t = matrix_c.copy()
        matrix_c_t = matrix_b.copy()
        dual_is_maximize = not is_maximize
        dual_signs = []
        for i in range(len(matrix_c)):
            if dual_is_maximize:
                dual_signs.append('<=')
            else:
                dual_signs.append('>=')
        if is_to_console:
            self.print_dual_system(matrix_a_t, matrix_b_t, matrix_c_t, dual_signs, dual_is_maximize)
        else:
            self.print_dual_system_to_file(matrix_a_t, matrix_b_t, matrix_c_t, dual_signs, dual_is_maximize, self.filename)
        for i in range(len(matrix_b_t)):
            if matrix_b_t[i] < 0:
                for j in range(len(matrix_c_t)):
                    matrix_a_t[i][j] = -matrix_a_t[i][j]
                matrix_b_t[i] = -matrix_b_t[i]
                if dual_signs[i] == '>=':
                    dual_signs[i] = '<='
                elif dual_signs[i] == '<=':
                    dual_signs[i] = '>='
        self.table = ArtificialBasis(matrix_a_t, matrix_b_t, matrix_c_t, dual_signs, dual_is_maximize, 'y')

    @staticmethod
    def print_dual_system(matrix_a: list, matrix_b: list, matrix_c: list, signs: list, is_maximize: bool):
        print('Dual system:')
        for i in range(len(matrix_a)):
            for j in range(len(matrix_b)):
                if j == 0 or matrix_a[i][j] < 0:
                    if matrix_a[i][j] == -1:
                        print('-y{}'.format(j + 1), end='')
                    elif matrix_a[i][j] == 1:
                        print('y{}'.format(j + 1), end='')
                    else:
                        print('{}y{}'.format(matrix_a[i][j], j + 1), end='')
                else:
                    if matrix_a[i][j] == 1:
                        print('+y{}'.format(j + 1), end='')
                    else:
                        print('+{}y{}'.format(matrix_a[i][j], j + 1), end='')
            print('{}{}'.format(signs[i], matrix_b[i]))
        print('Z(y)=', end='')
        for i in range(len(matrix_b)):
            if i == 0 or matrix_c[i] < 0:
                if matrix_c[i] == -1:
                    print('-y{}'.format(i + 1), end='')
                elif matrix_c[i] == 1:
                    print('y{}'.format(i + 1), end='')
                else:
                    print('{}y{}'.format(matrix_c[i], i + 1), end='')
            else:
                if matrix_c[i] == 1:
                    print('+y{}'.format(i + 1), end='')
                else:
                    print('+{}y{}'.format(matrix_c[i], i + 1), end='')
        if is_maximize:
            print(' -> max')
        else:
            print(' -> min')

    @staticmethod
    def print_dual_system_to_file(matrix_a: list, matrix_b: list, matrix_c: list, signs: list, is_maximize: bool, filename: str):
        file = open(filename, 'a')
        file.write('Dual system:\n')
        for i in range(len(matrix_a)):
            for j in range(len(matrix_b)):
                if j == 0 or matrix_a[i][j] < 0:
                    if matrix_a[i][j] == -1:
                        file.write('-y{}'.format(j + 1))
                    elif matrix_a[i][j] == 1:
                        file.write('y{}'.format(j + 1))
                    else:
                        file.write('{}y{}'.format(matrix_a[i][j], j + 1))
                else:
                    if matrix_a[i][j] == 1:
                        file.write('+y{}'.format(j + 1))
                    else:
                        file.write('+{}y{}'.format(matrix_a[i][j], j + 1))
            file.write('{}{}\n'.format(signs[i], matrix_b[i]))
        file.write('Z(y)=')
        for i in range(len(matrix_b)):
            if i == 0 or matrix_c[i] < 0:
                if matrix_c[i] == -1:
                    file.write('-y{}'.format(i + 1))
                elif matrix_c[i] == 1:
                    file.write('y{}'.format(i + 1))
                else:
                    file.write('{}y{}'.format(matrix_c[i], i + 1))
            else:
                if matrix_c[i] == 1:
                    file.write('+y{}'.format(i + 1))
                else:
                    file.write('+{}y{}'.format(matrix_c[i], i + 1))
        if is_maximize:
            file.write(' -> max\n')
        else:
            file.write(' -> min\n')
        file.close()

    def iterate(self):
        return self.table.iterate()

    def print(self):
        self.table.print()

    def can_be_iterated(self):
        return self.table.can_be_iterated()

    def drop_artificial_function(self):
        self.table.drop_artificial_function()

    def get_vector_answer(self):
        return self.table.get_vector_answer()

    def get_function_answer(self):
        return self.table.get_function_answer()

    def get_table_to_print(self):
        return self.table.get_table_to_print()
