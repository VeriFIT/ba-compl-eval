#!/usr/bin/env python3
# A script for translation of a standard Buchi automaton in the Hanoi Omega
# Automata format to Rabit's BA format.

import sys
import buchi_conv_common as BA


###########################################
if __name__ == '__main__':
    argc = len(sys.argv)
    if argc == 1:
        fd = sys.stdin
    elif argc == 2:
        fd = open(sys.argv[1], "r")
    else:
        print("Invalid number of arguments: either 0 or 1 required")
        sys.exit(1)

    aut = BA.parseHOA(fd)
    res = BA.aut2BA(aut)

    print(res, end="")

    if argc == 2:
        fd.close()
