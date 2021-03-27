import RandomClass, argparse


# TODO: remove arg parse of boundaries, arguments limits

class Decoder:
    '''Класс со всем необходимым для расшифровки файла'''

    def __init__(self):
        '''Конструктор класса, без параметров'''
        self.parser = argparse.ArgumentParser(
            description='Block cipher decoder, that should be invulnerable to bruteforce.')
        self.random = RandomClass.Random()  # Ключевой генератор чисел
        self.grid = list()  # Таблица 8 на 8 ячеек по 1 байту
        self.grid_pos = 0  # Номер текущего бита
        self.attempts = list()  # Количество попыток
        self.max_depth = -1  # Максимальная глубина рекурсии
        self.cur_depth = 0  # Текущая глубина рекурсии
        self.min_num = 200  # Минимальное количество попыток
        self.stack = list()  # Стэк для функций шифрования
        self.file_data = bytearray()  # Информация из зашифрованного файла
        self.output_file = str()  # Имя выходного файла
        self.decoded_bits = str()  # Расшифрованные биты
        self.key = int()  # Ключ для ключевого генератора
        self.ops = {  # Функции перемешивания
            0: self.random_func,  # Cлучайная функия из ops
            1: self.plus_op,  # Увеличить op на один данной ячейки
            2: self.shift_rows,  # Сдвинуть циклически все строки в grid
            3: self.goto_from_beg,  # Выполнить операцию начиная отсчет с начала grid
            4: self.xor,  # Произвести xor ячейки в зависимости от текущей ячейки и числа из ключевого генератора
            5: self.swap_cell,  # Поменять ячейки местами в зависимости от текущей ячейки
            6: self.if_false,  # Выполняет операцию в зависимости от значения ячейки и числа из ключевого генератора
            7: self.if_true,  # Выполняет операцию в зависимости от значения ячейки и  числа из ключевого генератора
            8: self.plus_data,  # Увеличивает data на 1 в текущей ячейке
            9: self.xor_row,  # Производит xor всех значений строки со случайным числом из ключевого генератора
            10: self.swap_cols,  # Меняет колонки в grid местами
            11: self.swap_rows,  # Меняет строки в grid местами
            12: self.goto_from_end,  # Выполнить операцию начиная отсчет с конца grid
            13: self.xor_col,  # Производит xor всех значений колонки со случайным числом из ключевого генератора
            14: self.xor,  # Произвести xor ячейки в зависимости от текущей ячейки и числа из ключевого генератора
            15: self.random_func  # Cлучайная функия из ops
        }
        self.stack = list()  # Стэк для функций шифрования
        # Параметры программы
        self.parser.add_argument('-v', '--verbose', help='prints info of all operations', action='store_true')
        self.parser.add_argument('-o', '--out', help='name of output file, default=decoded.txt', default='decoded.txt',
                                 type=str)
        self.parser.add_argument('-i', '--input', help='name of input file to be encoded, default=encoded.txt',
                                 default='encoded.txt', type=str)
        self.parser.add_argument('key', help='key for cipher')
        self.parser.add_argument('--version', help='prints version of script')

    def parse_args(self, args):
        '''Обработка входных параметров'''
        self.args = args
        args = self.parser.parse_args(args[1:])
        if args.version:
            print('Decoder version: 2.0')
            exit(0)
        self.random = RandomClass.Random()  # Создание ключевого генератора
        self.set_key(args.key)  # Обработка ключа для ключевого генератора
        self.verbose = args.verbose  # Параметр определяющий количество выводимой в консоль информации
        self.output_file = args.out  # Название выходного файла
        if not args.input:
            print("No data to be decoded was provided")
            exit(-1)
        self.parse_file(args.input)  # Обработка входного файла
        if self.verbose:
            print('Arguments are parsed. Parsing file.')

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

    def set_min_num(self, num, bounds):
        '''Получение min_num из ключевого генератора'''
        if num != -2:
            self.min_num = num
        else:
            self.min_num = self.random.randint(min(abs(bounds[0]), abs(bounds[1])), max(abs(bounds[0]), abs(bounds[1])))

    def parse_file(self, file):
        '''Получение входной информации'''
        self.file_data = open(file, 'rb').read()

    def decode_file_data(self):
        '''Обработка входного файла'''
        i = 0
        temp = 0
        temp2 = 0
        # Парсинг min_depth
        while self.file_data[i] != 255:
            temp += self.file_data[i]
            i += 1
        i += 1  # 255
        temp += self.file_data[i]
        i += 1
        # Парсинг max_depth
        while self.file_data[i] != 255:
            temp2 += self.file_data[i]
            i += 1
        i += 1  # 255
        temp2 += self.file_data[i]
        i += 1
        self.set_max_depth(-2, (temp, temp2))
        temp = 0
        temp2 = 0
        # Парсинг min_num
        while self.file_data[i] != 255:
            temp += self.file_data[i]
            i += 1
        i += 1  # 255
        temp += self.file_data[i]
        i += 1
        # parse max num
        while self.file_data[i] != 255:
            temp2 += self.file_data[i]
            i += 1
        i += 1  # 255
        temp2 += self.file_data[i]
        i += 1
        self.set_min_num(-2, (temp, temp2))
        # Парсинг len(binary_text)
        temp = 0
        while self.file_data[i] != 255:
            temp += self.file_data[i]
            i += 1
        i += 1
        temp += self.file_data[i]
        i += 1
        # Парсинг grid
        for j in range(temp):
            self.grid.append(list())
            for h in range(8):
                self.grid[j].append(list())
                for w in range(8):
                    self.grid[j][h].append(self.file_data[i + j * 64 + h * 8 + w])
        i += temp * 64
        # Парсинг attempts
        while i < len(self.file_data):
            temp = self.min_num
            while self.file_data[i] != 255:
                temp += self.file_data[i]
                i += 1
            i += 1
            temp += self.file_data[i]
            i += 1
            self.attempts.append(temp)

    def decode(self):
        '''Дешифровка файла'''
        self.decode_file_data()
        if self.verbose:
            print('File parsed. Starting decoding.')
        for self.grid_pos in range(len(self.grid)):  # Декодирование каждого бита
            check = self.random.randint(0, 64)
            for attempt in range(self.attempts[self.grid_pos]):
                entry = self.random.randint(0, 64)  # Выбор входной ячейки
                self.cur_depth = 0
                self.func_handler(entry)  # Выполнение функций в ячейке
                self.complete_func()
                check = self.random.randint(0, 64)  # Специальная пустая трата вызова random
            if self.verbose:
                print(f'Bit decoded. Progress: {round(float(self.grid_pos + 1) / len(self.grid) * 100)}%')
            # Сборка полученных битов
            self.decoded_bits = self.decoded_bits + str(self.grid[self.grid_pos][check // 8][check % 8] & 1)
        if self.verbose:
            print('Saving output.')
        self.save()  # Сохранение файла
        if self.verbose:
            print('Output saved. Exiting.')

    def save(self):
        '''Сохранение расшифрованной информации'''
        out = bytearray()
        for i in range(len(self.decoded_bits) // 8):
            out.append(int(self.decoded_bits[i * 8:i * 8 + 8], 2))
        f = open(self.output_file, mode='wb+')
        f.write(out)
        f.close()

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
