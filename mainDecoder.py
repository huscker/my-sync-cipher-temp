import decoder, sys

if __name__ == '__main__':
    args = sys.argv[1:]
    main_decoder = decoder.Decoder()
    main_decoder.parse_args(args)
    main_decoder.decode()
