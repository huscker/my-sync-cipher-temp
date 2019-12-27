import random, RandomClass


class Decoder:
    def __init__(self, args):
        self.random_ch = 2
        self.grid = list()
        self.grid_pos = 0
        self.attempts = list()
        self.max_depth = -1
        self.min_num = 200
        self.stack = list()
        self.temp_grid = list()
        self.file_data = bytearray()
        self.file_input_data = str()
        self.output_file = str()
        self.decoded_bits = str()
        self.interactive = False
        self.ops = {
            0: self.random_func,
            1: self.plus_op,
            2: self.shift_rows,
            3: self.goto_from_beg,
            4: self.xor,
            5: self.swap_cell,
            6: self.if_false,
            7: self.if_true,
            8: self.plus_data,
            9: self.xor_row,
            10: self.swap_cols,
            11: self.swap_rows,
            12: self.goto_from_end,
            13: self.xor_col,
            14: self.xor,
            15: self.random_func
        }
        self.args = args
        self.stack = list()
        self.parse_args()

    def parse_args(self):
        for i in range(len(self.args)):
            if self.args[i] == '-k':
                self.key = self.args[i + 1]
            elif self.args[i] == '-i':
                self.interactive = True
            elif self.args[i] == '-I':
                self.parse_input_file(self.args[i + 1])
            elif self.args[i] == '-f':
                self.parse_file(self.args[i + 1])
            elif self.args[i] == '-d':
                self.max_depth = int(self.args[i + 1])
            elif self.args[i] == '-m':
                self.min_num = int(self.args[i + 1])
            elif self.args[i] == '-r':
                self.random_ch = self.args[i + 1]
            elif self.args[i] == '-o':
                self.output_file = self.args[i + 1]

    # key file - file_input_data
    # file - filedata

    def parse_file(self, file):
        self.file_data = open(file, 'rb').read()
        self.decode_file_data()

    def parse_input_file(self, file):
        self.file_input_data = open(file, 'r', encoding='utf8').read()

    def random_choice(self, num):
        if int(num) == 1:
            self.random = random.random()
            self.random.seed(self.key)
        elif int(num) == 2:
            self.random == RandomClass.Random()
            self.random.seed(int(self.key))

    def decode_file_data(self):
        if self.interactive:
            i = 0
            temp = 0
            while self.file_data[i] != 255:
                temp += self.file_data[i]
                i += 1
            i += 1
            temp += self.file_data[i]
            i += 1
            for j in range(temp):
                self.grid.append(list())
                for h in range(8):
                    self.grid[j].append(list())
                    for w in range(8):
                        self.grid[j][h].append(self.file_data[i + j * 64 + h * 8 + w])
        else:
            i = 0
            temp = 0
            while self.file_data[i] != 255:
                temp += self.file_data[i]
                i += 1
            i += 1
            temp += self.file_data[i]
            i += 1
            for j in range(temp):
                self.grid.append(list())
                for h in range(8):
                    self.grid[j].append(list())
                    for w in range(8):
                        self.grid[j][h].append(self.file_data[i + j * 64 + h * 8 + w])
            i += temp * 64
            while i < len(self.file_data):
                temp = self.min_num
                while self.file_data[i] != 255:
                    temp += self.file_data[i]
                    i += 1
                i += 1
                temp += self.file_data[i]
                self.attempts.append(temp)

    def decode(self):

        if self.interactive:
            temp = self.file_input_data.split('-1')
            self.key = temp[0]
            self.random_choice(self.random_ch)
            temp = temp[1:]
            self.grid_pos = 0
            for i in temp:
                t = i.split(',')
                entry = int(t[-1])
                for j in range((len(t) - 1) // 2):
                    entr = t[j * 2]
                    self.max_depth = t[j * 2 + 1]
                    self.func_handler(entry, 0)
                    self.complete_func()

                self.decoded_bits = self.decoded_bits + str(self.grid_pos[self.grid_pos][entry // 8][entry % 8] & 1)
                self.grid_pos += 1
            self.save()



        else:
            self.random_choice(self.random_ch)
            for self.grid_pos in range(len(self.grid)):
                entry = self.random.randint(0, 64)
                for attempt in range(len(self.attempts[self.grid_pos])):
                    entry = self.random.randint(0, 64)
                    self.func_handler(entry, 0)
                    self.complete_func()
                    check = self.random.randint(0, 64)  # чтобы потрать random call
                self.decoded_bits = self.decoded_bits + str(self.grid[self.grid_pos][check // 8][check % 8] & 1)

    def save(self):
        out = bytearray()
        for i in range(len(self.decoded_bits) // 8):
            out.append(int(self.decoded_bits[i * 8:i * 8 + 8], 2))
        f = open(self.output_file, mode='wb+')
        f.write(out)
        out.close()

    def complete_func(self):
        while len(self.stack) > 0:
            temp = self.stack.pop()
            temp[0](temp[1], temp[2])

    def func_handler(self, pos, depth, func=None):  #
        if self.max_depth == -1 or depth <= self.max_depth:
            h = (pos % 64) // 8
            w = pos % 8
            depth += 1
            if func is None:
                op = self.get_op(self.grid[self.grid_pos][h][w])
                data = self.get_data(self.grid[self.grid_pos][h][w])
                next_pos = (pos + 1) % 64
                t_list = list()
                t_list.append(self.ops[op])
                t_list.append(next_pos)
                t_list.append(depth)
                self.stack.append(t_list)
                next_pos = (next_pos + 1) % 64
                t_list = list()
                t_list.append(self.ops[data])
                t_list.append(next_pos)
                t_list.append(depth)
                self.stack.append(t_list)
            else:
                t_list = list()
                t_list.append(self.ops[func])
                t_list.append(pos)
                t_list.append(depth)
                self.stack.append(t_list)

    def num_to_bin(self, num):
        return '{:0>8}'.format(bin(num)[2:])

    def get_op(self, num):
        t = self.num_to_bin(num)
        return int(t[0] + t[2] + t[4] + t[6], 2)

    def set_op(self, num, n):
        t = list(self.num_to_bin(num))
        t2 = self.num_to_bin(n)
        t[0] = t2[4]
        t[2] = t2[5]
        t[4] = t2[6]
        t[6] = t2[7]
        return int(''.join(t), 2)

    def get_data(self, num):
        t = self.num_to_bin(num)
        return int(t[1] + t[3] + t[5] + t[7], 2)

    def set_data(self, num, n):
        t = list(self.num_to_bin(num))
        t2 = self.num_to_bin(n)
        t[1] = t2[4]
        t[3] = t2[5]
        t[5] = t2[6]
        t[7] = t2[7]
        return int(''.join(t), 2)

    def shift_rows(self, pos, depth):
        for h in range(8):
            self.grid[self.grid_pos][h] = self.grid[self.grid_pos][h][h:] + self.grid[self.grid_pos][h][:h]

    def plus_op(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        t = self.get_op(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_op(self.grid[self.grid_pos][h][w], t)

    def plus_data(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        t = self.get_data(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_data(self.grid[self.grid_pos][h][w], t)

    def xor(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        num = random.randint(0, 255)
        self.grid[self.grid_pos][h2][w2] ^= num

    def swap_rows(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        h1 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        h2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        self.grid[self.grid_pos][h1], self.grid[self.grid_pos][h2] = self.grid[self.grid_pos][h2], \
                                                                     self.grid[self.grid_pos][h1]

    def swap_cols(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        w1 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        for i in range(8):
            self.grid[self.grid_pos][i][w1], self.grid[self.grid_pos][i][w2] = self.grid[self.grid_pos][i][w2], \
                                                                               self.grid[self.grid_pos][i][w1]

    def swap_cell(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        self.grid[self.grid_pos][h][w], self.grid[self.grid_pos][h2][w2] = self.grid[self.grid_pos][h2][w2], \
                                                                           self.grid[self.grid_pos][h][w]

    def if_true(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = random.randint(0, 15)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) == 0:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos, depth + 1)
        else:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos, depth + 1)

    def if_false(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = random.randint(0, 15)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) == 0:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos, depth + 1)
        else:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos, depth + 1)

    def goto_from_beg(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        next_pos = self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos, depth + 1)

    def goto_from_end(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        next_pos = 63 - self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos, depth + 1)

    def random_func(self, pos, depth):
        self.func_handler(pos, depth + 1, func=random.randint(0, 15))

    def xor_row(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = random.randint(0, 255)
        h2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][h2][i] ^= num

    def xor_col(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = random.randint(0, 255)
        w2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][i][w2] ^= num
