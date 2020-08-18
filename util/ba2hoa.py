#!/usr/bin/env python3
# A script for translation of a standard Buchi automaton in Rabit's BA format
# into the Hanoi Omega Automata format.

import sys
from parse_ba import parseBA, aut2BA, aut2HOA




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

    aut = parseBA(fd)
    print(aut2HOA(aut), end="")

    if argc == 2:
        fd.close()
