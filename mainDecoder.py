import decoder, sys

if __name__ == '__main__':
    main_decoder = decoder.Decoder()
    main_decoder.parse_args(sys.argv)
    main_decoder.decode()
