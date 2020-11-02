#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import defaultdict


ngram_size = int(sys.argv[1])
infile = sys.argv[2]
outfile = sys.argv[3]

ngram = {}
context_freq = defaultdict(int)
n_1_freq = defaultdict(int)
relative_prob = {}


with open(infile, 'r') as inf:
    text = inf.read()
    for i in range(len(text) - ngram_size + 1):
        ng = text[i:i + ngram_size]
        ngram[ng] += 1

def compute_discount(ng_dict):
    N1 = sum(1 for x in ngram.values() if x == 1)
    N2 = sum(1 for y in ngram.values() if y == 2)

    if N1 < 100:
        return 0.5

    else:
        discount = N1 / N1 + (2 * N2)

    return discount


for _ in range(ngram_size):
    for n, v in ngram.items():
        context = n[:-1]
        context_freq[context] += v
        relative = n[1:]
        n_1_freq[relative] += v

    for n in ngram:
        ct = n[:-1]
        p = n - compute_discount(ngram) / context_freq[ct]
        relative_prob[n] += p

    ngram = n_1_freq

with open(outfile, 'wt') as op:
    json.dump(relative_prob, op)
