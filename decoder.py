import random, RandomClass,argparse


class Decoder:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Block cipher decoder, that should be invulnerable to bruteforce.')
        self.random = RandomClass.Random()
        self.random_ch = 2
        self.grid = list()
        self.grid_pos = 0
        self.attempts = list()
        self.max_depth = -1
        self.cur_depth = 0
        self.min_num = 200
        self.stack = list()
        self.temp_grid = list()
        self.file_data = bytearray()
        self.file_input_data = str()
        self.output_file = str()
        self.decoded_bits = str()
        self.key = int()
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
        self.stack = list()
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
        self.parser.add_argument('--depth',
                                 help='(advanced) sets recursion depth of algorithm, -1 = infinity,default = -1',
                                 type=int, default=-1)
        self.parser.add_argument('--num', help='(advanced) sets number of iterations per bit, default = 200',
                                 type=int, default=200)
        self.parser.add_argument('-o', '--out', help='name of output file, default=decoded.txt', default='decoded.txt',
                                 type=str)
        self.parser.add_argument('-i', '--input', help='name of input file to be encoded, default=encoded.txt',default='encoded.txt',type=str)
        self.parser.add_argument('-r', '--randomizer',
                                 help='(advanced) sets random generator to encode text, 1 - Python random library, 2 - Mersenne Twister by yinengy, default =2',
                                 choices=[1, 2], default=2)
        self.parser.add_argument('key', help='key for cipher')
        self.parser.add_argument('--version', help='prints version of script')

    def parse_args(self,args):
        self.args = args
        args = self.parser.parse_args(args[1:])
        if args.version:
            print('Decoder version: 1.1')
            exit(0)
        self.verbose = args.verbose
        self.set_max_depth(args.depth,(args.min_depth,args.max_depth))
        self.set_key(args.key)
        self.set_min_num(args.num,(args.min_num,args.max_num))
        self.output_file = args.out
        self.random_ch = args.randomizer
        if not args.input:
            print("No data to be decoded was provided")
            exit(-1)
        self.parse_file(args.input)
        """
                for i in range(len(self.args)):
            if self.args[i] == '-k':
                self.key = self.args[i + 1]
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
        """
        if self.verbose:
            print('Arguments are parsed. Parsing file.')

    # key file - file_input_data
    # file - filedata

    def set_max_depth(self, depth,bounds):
        if depth:
            self.max_depth = depth
        else:
            self.max_depth = self.random.randint(min(abs(bounds[0]),abs(bounds[1])),max(abs(bounds[0]),abs(bounds[1])))

    def set_key(self, key):
        if key:
            self.random.seed(int(key))
            self.key = key

    def set_min_num(self, num,bounds):
        if num:
            self.min_num = num
        else:
            self.min_num = self.random.randint(min(abs(bounds[0]),abs(bounds[1])),max(abs(bounds[0]),abs(bounds[1])))

    def parse_file(self, file):
        self.file_data = open(file, 'rb').read()


    def random_choice(self, num):
        if int(num) == 1:
            self.random = random.random()
            self.random.seed(self.key)
        elif int(num) == 2:
            self.random = RandomClass.Random()
            self.random.seed(int(self.key))
        else:
            self.random = RandomClass.Random()
            self.random.seed(int(self.key))

    def decode_file_data(self):
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
            i += 1
            self.attempts.append(temp)
    def decode(self):
        self.decode_file_data()
        self.random_choice(self.random_ch)
        if self.verbose:
            print('File parsed. Starting decoding.')
        for self.grid_pos in range(len(self.grid)):
            check = self.random.randint(0, 64)
            for attempt in range(self.attempts[self.grid_pos]):
                entry = self.random.randint(0, 64)
                # print(entry,end=' ')
                self.cur_depth = 0
                self.func_handler(entry)
                self.complete_func()
                check = self.random.randint(0, 64)  # чтобы потрать random call
            if self.verbose:
                print(f'Bit decoded. Progress: {round(float(self.grid_pos+1)/len(self.grid)*100)}%')
            self.decoded_bits = self.decoded_bits + str(self.grid[self.grid_pos][check // 8][check % 8] & 1)
        if self.verbose:
            print('Saving output.')
        self.save()
        if self.verbose:
            print('Output saved. Exiting.')
    def save(self):
        out = bytearray()
        for i in range(len(self.decoded_bits) // 8):
            out.append(int(self.decoded_bits[i * 8:i * 8 + 8], 2))
        f = open(self.output_file, mode='wb+')
        f.write(out)
        f.close()

    def complete_func(self):
        while len(self.stack) > 0:
            temp = self.stack.pop()
            temp[0](temp[1])

    def func_handler(self, pos, func=None):  #
        if self.max_depth == -1 or self.cur_depth <= self.max_depth:
            h = (pos % 64) // 8
            w = pos % 8
            self.cur_depth += 1
            if func is None:
                op = self.get_op(self.grid[self.grid_pos][h][w])
                data = self.get_data(self.grid[self.grid_pos][h][w])
                self.stack.append([self.ops[op], (pos + 1) % 64])
                self.stack.append([self.ops[data], (pos + 2) % 64])
            else:
                self.stack.append([self.ops[func], pos])

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

    def shift_rows(self, pos):
        for h in range(8):
            self.grid[self.grid_pos][h] = self.grid[self.grid_pos][h][h:] + self.grid[self.grid_pos][h][:h]

    def plus_op(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        t = self.get_op(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_op(self.grid[self.grid_pos][h][w], t)

    def plus_data(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        t = self.get_data(self.grid[self.grid_pos][h][w])
        t += 1
        if t >= 16:
            t -= 16
        self.grid[self.grid_pos][h][w] = self.set_data(self.grid[self.grid_pos][h][w], t)

    def xor(self, pos):  # ATTENTION WEIRD FUNC
        h = (pos % 64) // 8
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        num = self.random.randint(0, 256)
        self.grid[self.grid_pos][h2][w2] ^= num

    def swap_rows(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        h1 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        h2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        self.grid[self.grid_pos][h1], self.grid[self.grid_pos][h2] = self.grid[self.grid_pos][h2], \
                                                                     self.grid[self.grid_pos][h1]

    def swap_cols(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        w1 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        for i in range(8):
            self.grid[self.grid_pos][i][w1], self.grid[self.grid_pos][i][w2] = self.grid[self.grid_pos][i][w2], \
                                                                               self.grid[self.grid_pos][i][w1]

    def swap_cell(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        self.grid[self.grid_pos][h][w], self.grid[self.grid_pos][h2][w2] = self.grid[self.grid_pos][h2][w2], \
                                                                           self.grid[self.grid_pos][h][w]

    def if_true(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 16)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) == 0:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos)
        else:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos)

    def if_false(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 16)
        dat = self.get_data(self.grid[self.grid_pos][h][w])
        if (max(num, dat) + 1) % (min(num, dat) + 1) == 0:
            next_pos = pos + 2
            next_pos = next_pos % 64
            self.func_handler(next_pos)
        else:
            next_pos = pos + 1
            next_pos = next_pos % 64
            self.func_handler(next_pos)

    def goto_from_beg(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        next_pos = self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos)

    def goto_from_end(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        next_pos = 63 - self.grid[self.grid_pos][h][w] % 64
        self.func_handler(next_pos)

    def random_func(self, pos):
        self.func_handler(pos, func=self.random.randint(0, 16))

    def xor_row(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 256)
        h2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][h2][i] ^= num

    def xor_col(self, pos):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 256)
        w2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][i][w2] ^= num
