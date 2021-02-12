#!/usr/bin/env python3
# A script for translation of a standard Buchi automaton in Rabit's BA format
# into the Hanoi Omega Automata format.

import argparse
import fileinput
import sys
import buchi_conv_common as BA

ENCODING_CHOICES = {"binary": "BINARY_NONEXHAUSTIVE",
                    "binary_exhaust": "BINARY_EXHAUSTIVE",
                    "one_hot": "ONE_HOT"
                   }

###########################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description="converts Buchi automata from BA to HOA format")
    parser.add_argument("file", nargs="?",
                        help="input file with an automaton in the BA format",
                        type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-e', '--encoding', metavar='ENCODING', type=str,
                        choices=ENCODING_CHOICES.keys(),
                        default="binary",
                        help=f"Which encoding to use. Options: {[str(enc) for enc in ENCODING_CHOICES.keys()]}")

    args = parser.parse_args()

    aut = BA.parseBA(args.file)
    res = BA.aut2HOA(aut, ENCODING_CHOICES[args.encoding])

    print(res, end="")
