import encoder, sys
import timeit

def f():
    main_encoder = encoder.Encoder()
    main_encoder.parse_args(sys.argv)
    main_encoder.encode()
if __name__ == '__main__':
    print('It took',timeit.timeit(f,number=1),'seconds')
