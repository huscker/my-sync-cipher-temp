import RandomClass, argparse


# TODO : add   arguments limits

class Encoder:
    '''Класс со всем необходимым для зашифрования файла'''
    def __init__(self):
        '''Конструктор класса, без параметров'''
        self.parser = argparse.ArgumentParser(description='Block cipher encoder, that is invulnerable to bruteforce.')
        self.random = RandomClass.Random() # Ключевой генератор чисел
        self.random_gen = RandomClass.Random() # Генератор случайных чисел треубемый для создания изначального grid
        self.grid = list() # Таблица 8 на 8 ячеек по 1 байту
        self.grid_pos = 0 # Номер текущего бита
        self.attempts = list() # Количество попыток
        self.max_depth = -1 # Максимальная глубина рекурсии
        self.max_depth_boundaries = (40, 10000) # Границы в пределах которых лежит max_depth
        self.cur_depth = 0 # Текущая глубина рекурсии
        self.min_num = 200 # Минимальное количество попыток
        self.min_num_boundaries = (50, 300) # Границы в пределах которых лежит min_num
        self.stack = list() # Стэк для функций шифрования
        self.temp_grid = list() # Изначальный grid
        self.file_data = bytearray() # Информация которая пойдет в зашифрованный файл
        self.output = str() # Название выходного файла
        self.binary_text = str() # Битовое представление текста
        self.key = int() # Ключ для ключевого генератора
        self.args = list() # Список входных параметров
        self.verbose = False # Переменная, ключающая вывод в консоль
        self.text = str() # Переменная для текста
        self.ops = {  # Функции перемешивания
            0: self.random_func,  # Cлучайная функия из ops
            1: self.plus_op,  # Увеличить op на один данной ячейки
            2: self.shift_rows, # Сдвинуть циклически все строки в grid
            3: self.goto_from_beg, # Выполнить операцию начиная отсчет с начала grid
            4: self.xor, # Произвести xor ячейки в зависимости от текущей ячейки и числа из ключевого генератора
            5: self.swap_cell, # Поменять ячейки местами в зависимости от текущей ячейки
            6: self.if_false, # Выполняет операцию в зависимости от значения ячейки и числа из ключевого генератора
            7: self.if_true, # Выполняет операцию в зависимости от значения ячейки и  числа из ключевого генератора
            8: self.plus_data, # Увеличивает data на 1 в текущей ячейке
            9: self.xor_row, # Производит xor всех значений строки со случайным числом из ключевого генератора
            10: self.swap_cols, # Меняет колонки в grid местами
            11: self.swap_rows, # Меняет строки в grid местами
            12: self.goto_from_end, # Выполнить операцию начиная отсчет с конца grid
            13: self.xor_col, # Производит xor всех значений колонки со случайным числом из ключевого генератора
            14: self.xor, # Произвести xor ячейки в зависимости от текущей ячейки и числа из ключевого генератора
            15: self.random_func  # Cлучайная функия из ops
        }
        # Параметры программы
        self.parser.add_argument('-v', '--verbose', help='prints info of all operations', action='store_true')
        self.parser.add_argument('-d', '--min-depth', help='sets minimum boundary for depth value, default = 40',
                                 type=int, default=40)
        self.parser.add_argument('-D', '--max-depth', help='sets maximum boundary for depth value, default = 10000',
                                 type=int, default=10000)
        self.parser.add_argument('-n', '--min_num',
                                 help='sets minimum boundary for number of iterations per bit, default = 50', type=int,
                                 default=50)
        self.parser.add_argument('-N', '--max_num',
                                 help='sets maximum boundary for number of iterations per bit, default = 300', type=int,
                                 default=300)
        self.parser.add_argument('--depth', help='(advanced) sets recursion depth of algorithm, -1 = infinity',
                                 type=int, default=-2)
        self.parser.add_argument('--num', help='(advanced) sets number of iterations per bit', type=int, default=-2)
        self.parser.add_argument('-t', '--text', help='input text to be encoded', type=str)
        self.parser.add_argument('-o', '--out', help='name of output file, default=encoded.txt', default='encoded.txt',
                                 type=str)
        self.parser.add_argument('-i', '--input', help='name of input file to be encoded', type=str)
        self.parser.add_argument('-g', '--gen_key', help='(advanced) sets seed for first field generation')
        self.parser.add_argument('key', help='key for cipher')
        self.parser.add_argument('--version', help='prints version of script')

    def parse_args(self, args):
        '''Обработка входных параметров'''
        self.args = args
        args = self.parser.parse_args(args[1:])
        if args.version:
            print('Encoder version: 2.0')
            exit(0)
        self.verbose = args.verbose  # Параметр определяющий количество выводимой в консоль информации
        self.random = RandomClass.Random()  # Создание ключевого генератора
        self.set_key(args.key)  # Обработка ключа для ключевого генератора
        self.set_max_depth(args.depth, (args.min_depth, args.max_depth))  # Получение max_depth
        self.max_depth_boundaries = (args.min_depth, args.max_depth)  # Границы в пределах которых лежит max_depth
        self.set_min_num(args.num, (args.min_num, args.max_num))  # Получение min_num
        self.min_num_boundaries = (args.min_num, args.max_num)  # Границы в пределах которых лежит min_num
        self.set_gen_key(args.gen_key)  # Обработка ключа для генератора изначального grid
        self.output = args.out  # Название выходного файла
        if not args.input and not args.text:
            print("No data to be encoded was provided")
            exit(-1)
        self.set_text(args.text)  # Обработка входного текста если он есть
        self.read_file(args.input)  # Обработка входного файла
        if self.verbose:
            print('Arguments are parsed. Filling cells.')

    def set_max_depth(self, depth, bounds):
        '''Получение max_depth из ключевого генератора'''
        if depth != -2:
            self.max_depth = depth
        else:
            self.max_depth = self.random.randint(min(abs(bounds[0]), abs(bounds[1])),
                                                 max(abs(bounds[0]), abs(bounds[1])))

    def set_key(self, key):
        '''Обработка ключа для ключевого генератора'''
        if key:
            self.random.seed(int(key))
            self.key = key

    def set_gen_key(self, key):
        '''Обработка ключа для генератора изначальнного grid'''
        if key:
            self.random_gen.seed(int(key))

    def set_min_num(self, num, bounds):
        '''Получение min_num из ключевого генератора'''
        if num != -2:
            self.min_num = num
        else:
            self.min_num = self.random.randint(min(abs(bounds[0]), abs(bounds[1])), max(abs(bounds[0]), abs(bounds[1])))

    def set_text(self, text):
        '''Обработка входного текста (не в файле)'''
        if text:
            self.text = text.encode('utf8')
            self.get_binary_text()
            self.prepare_grid()

    def read_file(self, file):
        '''Чтение входного файла'''
        if file:
            with open(file, mode='rb') as f:
                self.text = f.read()
            self.get_binary_text()
            self.prepare_grid()

    def get_binary_text(self):
        '''Получение текста в битовом представлении'''
        self.binary_text = ''
        for i in self.text:
            self.binary_text = self.binary_text + self.num_to_bin(i)

    def prepare_grid(self):
        '''Заполнение grid нулями'''
        for i in range(len(self.binary_text)):
            self.grid.append(list())
            for h in range(8):
                self.grid[i].append(list())
                for w in range(8):
                    self.grid[i][h].append(0)

    def fill_random_cell(self, g_pos):
        '''Заполнение изначального grid случайными числами не из ключевого генератора'''
        t_ops = list(range(16)) * 4
        t_data = list(range(16)) * 4
        t_ops = self.random_gen.shuffle(t_ops)
        t_data = self.random_gen.shuffle(t_data)
        for i in range(64):
            self.grid[g_pos][i // 8][i % 8] = self.set_op(self.grid[g_pos][i // 8][i % 8], t_ops[i])
            self.grid[g_pos][i // 8][i % 8] = self.set_data(self.grid[g_pos][i // 8][i % 8], t_data[i])

    def fill_random_cells(self):
        '''Заполнение grid случайными числами не ключевым генератором'''
        for g_pos in range(len(self.binary_text)):
            self.fill_random_cell(g_pos)

    def encode(self):
        '''Кодирование'''
        self.fill_random_cells()
        if self.verbose:
            print('Cells are filled.', 'Encoding started.', sep='\n')
        self.temp_grid.clear()  # Очистка полей и попыток
        self.attempts.clear()
        for self.grid_pos in range(len(self.grid)):  # Кодирование каждого бита
            self.copy_to_temp()  # Сохранение изначального grid
            self.complete_bit()
            if self.verbose:
                print(f'Bit encoded. Progress: {round(float(self.grid_pos + 1) / len(self.grid) * 100)}%')
        self.prepare_output()  # Подготовка к сохранению
        if self.verbose:
            print('Output prepared. Saving output.')
        self.save()  # Сохранение
        if self.verbose:
            print('Output saved. Exiting.')

    def copy_to_temp(self):
        '''Копирование начального grid'''
        for i in range(64):
            self.temp_grid.append(self.grid[self.grid_pos][i // 8][i % 8])

    def prepare_output(self):
        '''Подготовление данных для сохранения в файл'''
        # min depth
        temp = self.max_depth_boundaries[0]
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)
        # max depth
        temp = self.max_depth_boundaries[1]
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)
        # min num
        temp = self.min_num_boundaries[0]
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)
        # max num
        temp = self.min_num_boundaries[1]
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)
        # len(bin_text)
        temp = len(self.binary_text)
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)
        # grid
        for i in self.temp_grid:
            self.file_data.append(i)
        # attemps
        for i in self.attempts:
            temp = i - self.min_num
            while temp > 254:
                self.file_data.append(254)
                temp -= 254
            self.file_data.append(255)
            self.file_data.append(temp)

    def save(self):
        '''Cохранение бинарных данных'''
        out = open(self.output, mode='wb+')
        out.write(self.file_data)
        out.close()

    def complete_bit(self):
        '''Шифрование одного бита'''
        attempt = 0  # Обнуление счетчика попыток
        check = self.random.randint(0, 64)  # Выбор стартовой позиции из ключевого генератора
        while attempt < self.min_num or self.grid[self.grid_pos][check // 8][check % 8] & 1 != int(
                self.binary_text[
                    self.grid_pos]):  # Пока не будет сделано минимальное количество попыток и бит текста не совпадет с остатком от деления следующеей ячейки
            attempt += 1
            entry = self.random.randint(0, 64)
            self.cur_depth = 0
            self.func_handler(entry)
            self.complete_func()  # Проход по случайной ячейке из ключевого генератора
            check = self.random.randint(0, 64)  # Выбор ячейки для проверки
        self.attempts.append(attempt)  # сохранение количества попыток на бит

    def complete_func(self):
        '''Выполняет последнюю функцию в стэке'''
        while len(self.stack) > 0:
            temp = self.stack.pop()
            temp[0](temp[1])

    def func_handler(self, pos, func=None):
        '''Обрабатывает выполнение функций в ячейке'''
        if self.max_depth == -1 or self.cur_depth <= self.max_depth:  # Условие выхода (bailout)
            h = (pos % 64) // 8  # Перевод номера ячейки в координаты
            w = pos % 8
            self.cur_depth += 1
            if func is None:
                # Если на вход не подается функция,
                # то в стэк записываются следующие две ячейки с функциями,
                # выбранными в зависимости от op и data изначальной ячейки
                op = self.get_op(self.grid[self.grid_pos][h][w])
                data = self.get_data(self.grid[self.grid_pos][h][w])
                self.stack.append([self.ops[op], (pos + 1) % 64])
                self.stack.append([self.ops[data], (pos + 2) % 64])
            else:
                self.stack.append([self.ops[func], pos])

    def num_to_bin(self, num):
        '''Возвращает строковое представление числа num в двоичном виде'''
        return '{:0>8}'.format(bin(num)[2:])

    def get_op(self, num):
        '''Возвращает op в числе num'''
        t = self.num_to_bin(num)
        return int(t[0] + t[2] + t[4] + t[6], 2)

    def set_op(self, num, n):
        '''Возвращает число num с измененным op на n'''
        t = list(self.num_to_bin(num))
        t2 = self.num_to_bin(n)
        t[0] = t2[4]
        t[2] = t2[5]
        t[4] = t2[6]
        t[6] = t2[7]
        return int(''.join(t), 2)

    def get_data(self, num):
        '''Возвращает data в числе num'''
        t = self.num_to_bin(num)
        return int(t[1] + t[3] + t[5] + t[7], 2)

    def set_data(self, num, n):
        '''Возвращает число num с измененной data на n'''
        t = list(self.num_to_bin(num))
        t2 = self.num_to_bin(n)
        t[1] = t2[4]
        t[3] = t2[5]
        t[5] = t2[6]
        t[7] = t2[7]
        return int(''.join(t), 2)

    def shift_rows(self, pos):
        '''Сдвигает циклически строки в grid'''
        for h in range(8):
            self.grid[self.grid_pos][h] = self.grid[self.grid_pos][h][h:] + self.grid[self.grid_pos][h][:h]

    def plus_op(self, pos):
        '''Увеличивает значение op в ячейке pos на 1'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        t = self.get_op(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_op(self.grid[self.grid_pos][h][w], t)

    def plus_data(self, pos):
        '''Увеличивает значение data в ячейке pos на 1'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        t = self.get_data(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_data(self.grid[self.grid_pos][h][w], t)

    def xor(self, pos):
        '''Производит xor ячейки со слуйчайным числом из ключевого генератора'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        num = self.random.randint(0, 256)
        self.grid[self.grid_pos][h2][w2] ^= num

    def swap_rows(self, pos):
        '''Меняет строки в grid местами'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        h1 = self.get_op(self.grid[self.grid_pos][h][w]) % 8  # Получение номера первой строки
        h2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8  # Получение номера второй строки
        self.grid[self.grid_pos][h1], self.grid[self.grid_pos][h2] = self.grid[self.grid_pos][h2], \
                                                                     self.grid[self.grid_pos][h1]

    def swap_cols(self, pos):
        '''Меняет колонки в grid местами'''
        h = (pos % 64) // 8  # перевод номера ячейки в координаты
        w = pos % 8
        w1 = self.get_data(self.grid[self.grid_pos][h][w]) % 8  # Получение номера первой колонки
        w2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8  # Получение номера второй колонки
        for i in range(8):
            self.grid[self.grid_pos][i][w1], self.grid[self.grid_pos][i][w2] = self.grid[self.grid_pos][i][w2], \
                                                                               self.grid[self.grid_pos][i][w1]

    def swap_cell(self, pos):
        '''Меняет две ячейки местами'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8  # Получение координат второй ячейки
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        self.grid[self.grid_pos][h][w], self.grid[self.grid_pos][h2][w2] = self.grid[self.grid_pos][h2][w2], \
                                                                           self.grid[self.grid_pos][h][w]

    def if_true(self, pos):
        '''Выполняет операцию в зависимости от значения ячейки и случайного числа из ключевого генератора'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        num = self.random.randint(0, 16)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) == 0:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos)  # При верном условии выполняется операция на следующей ячейке
        else:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos)  # При неверном условии выполняется операция на следующей ячейке

    def if_false(self, pos):
        '''Выполняет операцию в зависимости от значения ячейки и случайного числа из ключевого генератора'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        num = self.random.randint(0, 16)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) != 0:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos)  # При неверном условии выполняется операция на следующей ячейке
        else:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos)  # При верном условии выполняется операция на следующей ячейке

    def goto_from_beg(self, pos):
        '''Выполняет операцию на новой ячейке начиная отсчет с начала grid'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        next_pos = self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos)

    def goto_from_end(self, pos):
        '''Выполняет операцию на новой ячейке начиная отсчет с конца grid'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        next_pos = 63 - self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos)

    def random_func(self, pos):
        '''Выполняет случайную функцию в зависимости от случайного числа из ключевого генератора'''
        self.func_handler(pos, func=self.random.randint(0, 16))

    def xor_row(self, pos):
        '''Производит xor всех значений строки со случайным числом из ключевого генератора'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        num = self.random.randint(0, 256)
        h2 = self.grid[self.grid_pos][h][w] % 8  # Выбор строки
        for i in range(8):
            self.grid[self.grid_pos][h2][i] ^= num

    def xor_col(self, pos):
        '''Производит xor всех значений колонки со случайным числом из ключевого генератора'''
        h = (pos % 64) // 8  # Перевод номера ячейки в координаты
        w = pos % 8
        num = self.random.randint(0, 256)
        w2 = self.grid[self.grid_pos][h][w] % 8  # Выбор колонки
        for i in range(8):
            self.grid[self.grid_pos][i][w2] ^= num
