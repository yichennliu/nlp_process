import sys
from collections import defaultdict
import json
import os
import math

prob_file = sys.argv[1]
infile = sys.argv[2]

ngram_prob = {}
backoff = {}
ngram_size = 0

for lang in os.listdir("models"):
    with open('models/'+lang) as file:
        ngram_prob[lang] = json.load( prob_file )

    backoff[lang] = defaultdict(lambda: 1.0)
    for ngram, p in ngram_prob[lang].items():
        context = ngram[0:-1]
        backoff[lang][context] -= p
        if ngram_size < len(ngram):
            ngram_size = len(ngram)
print("done", file=sys.stderr)


with open(infile) as file:
    text = file.read()

def smoothed_prob( ngram, lang ):
    if len(ngram) == 0:
        return 1.0 / 1000
    context = ngram[0:-1]
    ngram2 = ngram[1:]
    p = ngram_prob[lang].get(ngram, 0.0)
    bof = backoff[lang].get(context, 1.0)
    bop = smoothed_prob(ngram2, lang)
    return p + bof * bop

text_length = len(text)
text = ' '*(ngram_size-1) + text

score = {}
for lang in ngram_prob:
    logp = 0.0
    for i in range(text_length):
        ngram = text[i:i+ngram_size]
        logp += math.log2(smoothed_prob(ngram, lang))

    # calculate cross entropy
    score[lang] = -logp / text_length


for lang in sorted(score.keys(), key=score.get):
    print(lang, score[lang], sep="\t")