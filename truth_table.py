#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
input_values = [i for i in itertools.product([0, 1], repeat = 5)]
print("set\tA  B  C  D  E  Y1  Y2")
i = 0
for A,B,C,D,E in input_values:
    y1 = not(not(A and C) and not(B and not(C and D)))
    y2 = not(not(not(C and D) and E) and not(B and not(C and D)))
    print(i, end="\t")
    print(A, end="  ")
    print(B, end="  ")
    print(C, end="  ")
    print(D, end="  ")
    print(E, end="  ")
    print(int(y1), end="  ")
    print(int(y2))
    i += 1
