import encoder, sys

if __name__ == '__main__':
    args = sys.argv[1:]
    main_encoder = encoder.Encoder()
    main_encoder.parse_args(args)
    main_encoder.encode()
