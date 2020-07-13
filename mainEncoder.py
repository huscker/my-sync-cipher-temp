import encoder, sys

if __name__ == '__main__':
    main_encoder = encoder.Encoder()
    main_encoder.parse_args(sys.argv)
    main_encoder.encode()
