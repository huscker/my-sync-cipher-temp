import encoder, sys

if __name__ == '__main__':
    args = sys.argv[1:]
    main_encoder = encoder.Encoder()
    debug = False
    for i in range(len(args)):
        if args[i] == '-d':
            main_encoder.set_max_depth(int(args[i + 1]))
        elif args[i] == '-k':
            main_encoder.set_key(args[i + 1])
        elif args[i] == '-g':
            main_encoder.set_gen_key(args[i + 1])
        elif args[i] == '-m':
            main_encoder.set_min_num(int(args[i + 1]))
        elif args[i] == '-t':
            main_encoder.set_text(args[i + 1])
        elif args[i] == '-f':
            main_encoder.read_file(args[i + 1])
        elif args[i] == '-o':
            main_encoder.output = args[i + 1]
        elif args[i] == '-O':
            main_encoder.output_key = args[i + 1]
        elif args[i] == '-i':
            main_encoder.interactive = True
        elif args[i] == '-D':
            debug = True
    if debug:
        main_encoder.fill_random_cells()
        main_encoder.print_grid()
    main_encoder.encode()
