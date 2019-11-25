import math, random, copy, hashlib


class Encoder:
    SIDE = 8
    GRID = SIDE ** 2
    M_E_P_C = 2 ** 8

    def __init__(self):
        self.random = random.Random()
        self.random_gen = random.Random()
        self.grid = list()
        self.grid_pos = 0
        self.attempts = list()
        self.max_depth = -1
        self.stack = list()
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

    def set_max_depth(self, depth):
        self.max_depth = depth

    def set_key(self, key):
        self.random.seed(key)

    def set_gen_key(self, key):
        self.gen_random.seed(key)

    def set_min_num(self, num):
        self.min_num = num

    def set_text(self, text):
        self.text = text.encode('utf8')
        self.get_binary_text()
        self.prepare_grid()

    def read_file(self, file):
        with open(file, mode='rb') as f:
            self.text = f.read()

    def get_binary_text(self):
        self.binary_text = ''
        for i in self.text:
            self.binary_text = self.binary_text + self.num_to_bin(i)

    def prepare_grid(self):
        for i in range(len(self.binary_text)):
            self.grid.append(list())
            for h in range(8):
                self.grid[i].append(list())
                for w in range(8):
                    self.grid[i][h].append(0)

    def print_grid(self):
        for i in range(len(self.grid)):
            for h in range(8):
                for w in range(8):
                    print(self.num_to_bin(self.grid[i][h][w]), end=' ')
                print()
            print()

    def fill_random_cell(self, g_pos):
        t_ops = list(range(16)) * 4
        t_data = list(range(16)) * 4
        random.shuffle(t_ops)
        random.shuffle(t_data)
        for i in range(64):
            self.grid[g_pos][i // 8][i % 8] = self.set_op(self.grid[g_pos][i // 8][i % 8], t_ops[i])
            self.grid[g_pos][i // 8][i % 8] = self.set_data(self.grid[g_pos][i // 8][i % 8], t_data[i])

    def fill_random_cells(self):
        for g_pos in range(len(self.binary_text)):
            self.fill_random_cell(g_pos)

    def encode(self):
        self.fill_random_cells()
        for self.grid_pos in range(len(self.grid)):
            self.complete_bit()

    def complete_bit(self):
        attempt = 0
        check = self.random.randint(0, 63)
        while attempt < self.min_num or self.grid[self.grid_pos][check // 8][check % 8] & 1 != self.binary_text[
            self.grid_pos]:
            attempt += 1
            entry = self.random.randint(0, 63)
            self.func_handler(entry, 0)
            self.complete_func()
            check = self.random.randint(0, 63)

        self.attempts.append(attempt)

    def complete_func(self):
        while len(self.stack) > 0:
            temp = self.stack.pop()
            temp[0](temp[1], temp[2])

    def testfill(self, g_pos):
        for i in range(64):
            self.grid[g_pos][i // 8][i % 8] = i

    # cipher funcs

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
                t_list.append(self.ops[op], next_pos, depth)
                self.stack.append(t_list)
                next_pos = (next_pos + 1) % 64
                t_list = list()
                t_list.append(self.ops[data], next_pos, depth)
                self.stack.append(t_list)
            else:
                t_list = list()
                t_list.append(self.ops[func], pos, depth)
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


a = Encoder()
a.set_text('h')
a.testfill(0)
a.grid[0][0][6] = 220
print(a.get_data(220), a.get_op(220))
