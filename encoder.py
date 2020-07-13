import math, random, copy, hashlib, logging, RandomClass,argparse



class Encoder:
    SIDE = 8
    GRID = SIDE ** 2

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Block cipher encoder, that should be invulnerable to bruteforce.')
        self.random = RandomClass.Random()
        self.random_gen = RandomClass.Random()
        self.grid = list()
        self.grid_pos = 0
        self.attempts = list()
        self.max_depth = -1
        self.min_num = 200
        self.stack = list()
        self.temp_grid = list()
        self.file_data = bytearray()
        self.output = str()
        self.output_key_file = str()
        self.output_key_data = bytearray()
        self.binary_text = str()
        self.key = str()
        self.args = list()
        self.random_ch = 2
        self.verbose = False
        self.text = str()
        self.ops = {
            0:self.random_func,
            1:self.plus_op,
            2:self.shift_rows,
            3:self.goto_from_beg,
            4:self.xor,
            5:self.swap_cell,
            6:self.if_false,
            7:self.if_true,
            8:self.plus_data,
            9:self.xor_row,
            10:self.swap_cols,
            11:self.swap_rows,
            12:self.goto_from_end,
            13:self.xor_col,
            14:self.xor,
            15:self.random_func
        }
        self.parser.add_argument('-v', '--verbose', help='prints info of all operations', action='store_true')
        self.parser.add_argument('-d', '--depth', help='(advanced) sets recursion depth of algorithm, -1 = infinity,default = -1',
                                 type=int, default=-1)
        self.parser.add_argument('-n', '--num', help='(advanced) sets number of iterations per bit, default = 200',type=int,default=200)
        self.parser.add_argument('-t', '--text', help='input text to be encoded',type=str)
        self.parser.add_argument('-o', '--out',help='name of output file, default=encoded.txt',default='encoded.txt',type=str)
        self.parser.add_argument('-i', '--input',help='name of input file to be encoded',type=str)
        self.parser.add_argument('-r', '--randomizer',help='(advanced) sets random generator to encode text, 1 - Python random library, 2 - Mersenne Twister by yinengy, default =2',choices=[1,2],default=2)
        self.parser.add_argument('-g', '--gen_key', help='(advanced) sets seed for first field generation')
        self.parser.add_argument('-p', '--profile', help='sets automatically depth and num, depth=50*value, num=10*value,default=8',default=8,type=int)
        self.parser.add_argument('key',help='key for cipher')
        self.parser.add_argument('--version', help='prints version of script')

    def parse_args(self,args):
        self.args = args
        args = self.parser.parse_args(args[1:])
        if args.version:
            print('Encoder version: 1.0')
            exit(0)
        self.verbose = args.verbose
        self.set_max_depth(args.depth)
        self.set_key(args.key)
        self.set_gen_key(args.gen_key)
        self.set_min_num(args.num)
        self.set_profile(args.profile)
        self.output = args.out
        self.random_ch = args.randomizer
        if not args.input and not args.text:
            print("No data to be encoded was provided")
            exit(-1)
        self.set_text(args.text)
        self.read_file(args.input)

        """
                for i in range(len(self.args)):
            if self.args[i] == '-d':
                self.set_max_depth(int(self.args[i + 1]))
            elif self.args[i] == '-k':
                self.set_key(self.args[i + 1])
            elif self.args[i] == '-g':
                self.set_gen_key(self.args[i + 1])
            elif self.args[i] == '-m':
                self.set_min_num(int(self.args[i + 1]))
            elif self.args[i] == '-t':
                self.set_text(self.args[i + 1])
            elif self.args[i] == '-f':
                self.read_file(self.args[i + 1])
            elif self.args[i] == '-o':
                self.output = self.args[i + 1]
            elif self.args[i] == '-O':
                self.output_key = self.args[i + 1]
            elif self.args[i] == '-r':
                self.random_ch = int(self.args[i+1])
        """
        if self.verbose:
            print('Arguments are parsed. Filling cells.')

    def set_profile(self,profile):
        if profile:
            self.max_depth = 50*profile
            self.min_num = 10*profile

    def set_max_depth(self, depth):
        if depth:
            self.max_depth = depth

    def set_key(self, key):
        if key:
            self.random.seed(int(key))
            self.key = key

    def set_gen_key(self, key):
        if key:
            self.random_gen.seed(int(key))

    def set_min_num(self, num):
        if num:
            self.min_num = num

    def set_text(self, text):
        if text:
            self.text = text.encode('utf8')
            self.get_binary_text()
            self.prepare_grid()

    def read_file(self, file):
        if file:
            with open(file, mode='rb') as f:
                self.text = f.read()
            self.get_binary_text()
            self.prepare_grid()

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

    def print_grid(self, choice=1):
        if choice == 1:
            for i in range(len(self.grid)):
                for h in range(8):
                    for w in range(8):
                        print(self.num_to_bin(self.grid[i][h][w]), end=' ')
                    print()
                print()
        elif choice == 2:
            for h in range(8):
                for w in range(8):
                    print(f'{h*8+w:02}:{self.num_to_bin(self.grid[self.grid_pos][h][w])}',end=' ')
                print()
            print()
        elif choice == 3:
            s = list()
            for i in range(64):
                if self.grid[self.grid_pos][i // 8][i % 8] & 1 != int(self.binary_text[self.grid_pos]):
                    s.append(str(i))
            print(f'check options: {",".join(s)}')
        elif choice == 4:
            print(self.grid)

    def fill_random_cell(self, g_pos):
        t_ops = list(range(16)) * 4
        t_data = list(range(16)) * 4
        t_ops = self.random_gen.shuffle(t_ops)
        t_data = self.random_gen.shuffle(t_data)
        for i in range(64):
            self.grid[g_pos][i // 8][i % 8] = self.set_op(self.grid[g_pos][i // 8][i % 8], t_ops[i])
            self.grid[g_pos][i // 8][i % 8] = self.set_data(self.grid[g_pos][i // 8][i % 8], t_data[i])

    def fill_random_cells(self):
        for g_pos in range(len(self.binary_text)):
            self.fill_random_cell(g_pos)

    def encode(self):
        completed = False
        self.fill_random_cells()
        if self.verbose:
            print('Cells are filled.','Encoding started.',sep='\n')
        # self.print_grid(4)
        while not completed:
            self.temp_grid.clear()
            self.attempts.clear()
            for self.grid_pos in range(len(self.grid)):
                self.copy_to_temp()
                self.complete_bit()
                if self.verbose:
                    print(f'Bit encoded. Progress: {round(float(self.grid_pos+1)/len(self.grid)*100)}%')
            completed = True
        self.prepare_output()
        if self.verbose:
            print('Output prepared. Saving output.')
        self.save()
        if self.verbose:
            print('Output saved. Exiting.')

    def copy_to_temp(self):
        for i in range(64):
            self.temp_grid.append(self.grid[self.grid_pos][i // 8][i % 8])

    def prepare_output(self):
        temp = len(self.binary_text)
        while temp > 254:
            self.file_data.append(254)
            temp -= 254
        self.file_data.append(255)
        self.file_data.append(temp)

        for i in self.temp_grid:  ####################
            self.file_data.append(i)

        for i in self.attempts:
            temp = i - self.min_num
            while temp > 254:
                self.file_data.append(254)
                temp -= 254
            self.file_data.append(255)
            self.file_data.append(temp)


    def save(self):
        out = open(self.output, mode='wb+')
        out.write(self.file_data)
        out.close()
    def complete_bit(self):
        attempt = 0
        check = self.random.randint(0, 64)
        while attempt < self.min_num or self.grid[self.grid_pos][check // 8][check % 8] & 1 != int(
                self.binary_text[self.grid_pos]):
            attempt += 1
            entry = self.random.randint(0, 64)
            self.func_handler(entry, 0)
            self.complete_func()
            check = self.random.randint(0, 64)
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

    def xor(self, pos, depth): # ATTENTION WEIRD FUNC
        h = (pos % 64) // 8
        w = pos % 8
        h2 = self.get_op(self.grid[self.grid_pos][h][w]) % 8
        w2 = self.get_data(self.grid[self.grid_pos][h][w]) % 8
        num = self.random.randint(0, 256)
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
        num = self.random.randint(0, 16)
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
        num = self.random.randint(0, 16)
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
        self.func_handler(pos, depth + 1, func=self.random.randint(0, 16))

    def xor_row(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 256)
        h2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][h2][i] ^= num

    def xor_col(self, pos, depth):
        h = (pos % 64) // 8
        w = pos % 8
        num = self.random.randint(0, 256)
        w2 = self.grid[self.grid_pos][h][w] % 8
        for i in range(8):
            self.grid[self.grid_pos][i][w2] ^= num


