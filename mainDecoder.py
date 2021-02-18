import decoder, sys,timeit

def f():
    main_decoder = decoder.Decoder()
    main_decoder.parse_args(sys.argv)
    main_decoder.decode()

if __name__ == '__main__':
    print(timeit.timeit(f, number=1))
