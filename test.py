import math, random, copy, hashlib

SIDE = 8
GRID = SIDE ** 2
M_E_P_C = 2 ** 8

grid = list()
entries = list()
coords = list()

grid_pos = 0


# entries + -1 + coord of char + -2
def get_entries_from_passwd(s, num):
    random.seed(hashlib.sha512((s + str(num)).encode()).hexdigest())
    a = list()
    for i in range(num):
        t = random.randint(0, M_E_P_C)
        for i in range(t):
            a.append(random.randint(0, GRID - 1))
        a.append(-1)
        a.append(random.randint(0, GRID - 1))
        a.append(-2)
    return a


def ultim_get_entries(s, num):
    random.seed(hashlib.sha512((s + str(num)).encode()).hexdigest())
    a = list()
    b = list()
    for i in range(num):
        t = random.randint(0, M_E_P_C)
        for i in range(t):
            a.append(random.randint(0, GRID - 1))
        a.append(-1)
        t = random.randint(0, GRID - 1)
        b.append(t)
        a.append(t)
        a.append(-2)
    return a, b


def prepare_grid(text):
    for i in range(len(text)):
        grid.append(list())
        for h in range(SIDE):
            grid[i].append(list())
            for w in range(SIDE):
                grid[i][h].append(0)


def place_chars(text, key):
    entries, coords = ultim_get_entries(key, len(grid))
    print(entries, coords)
    print(ultim_get_entries(key, len(grid)))
    for i in range(len(grid)):
        grid[i][coords[i] // SIDE][coords[i] % SIDE] = ord(text[i])


def make_grid(text, key):
    prepare_grid(text)
    place_chars(text, key)


def print_grid():
    for i in range(len(grid)):
        for h in range(SIDE):
            for w in range(SIDE):
                print(grid[i][h][w], end=' ')
            print()
        print()


# cipher funcs

def get_op(num):


def shift_rows(i=False):
    if i:
        for h in range(SIDE):
            grid[grid_pos][h] = grid[grid_pos][h][h:] + grid[grid_pos][h][:h]
    else:
        for h in range(SIDE):
            grid[grid_pos][h] = grid[grid_pos][h][-h:] + grid[grid_pos][h][:-h]


def plus_op(h, w, i=False):
    if i:
        grid[grid_pos][h][w]
    else:
        pass
