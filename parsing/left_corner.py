from collections import defaultdict
import sys

def read_file(infile):
    lexicon = defaultdict(lambda: defaultdict(int))
    with open(infile) as inf:
        for line in inf:
            p, lhs, *rhs = line.split()
            lexicon[rhs[0]][(lhs, tuple(rhs))] = p

    return lexicon


class Parser:

    def __init__(self, grammar, lexicon):
        self.grammar_file = read_file(grammar)
        self.lexicon_file = read_file(lexicon)

    def scan(self, word, pos):

        for (lhs, rhs), p in self.lexicon_file[word].items():
            self.add(lhs, rhs, 1, pos, pos+1, p, None)

    def predict(self, cat, startp, endp, logp, child):
        for cat in self.grammar_file:
            for lhs, rhs, p in self.grammar_file.items():
                self.add(lhs, rhs, 1, startp, endp, logp + p, child)

    def complete(self, cat, splitp, endp, logp, child):
       for lhs, rhs, punkt, startp, p in self.logvitp[splitp].items():
           if punkt < len(lhs) and rhs[punkt] == cat:
               self.add(lhs, rhs, punkt+1, startp, endp,logp + p, child)

    def add(self, lhs, rhs, dotp, startp, endp, logp, child):

        items = lhs, rhs, dotp, startp

        if items not in self.logvitp[endp] or self.logvitp[endp][items] < logp:
            self.logvitp[endp][items] = logp
            self.childitem[endp][items] = child
        if dotp == len(rhs):
            self.predict(lhs, startp, endp, logp, items)
            self.complete(lhs, startp, endp, logp, items)

    def print_children(self, item, endpos):

        lhs, rhs, dotpos, startpos = item
        child = self.childitem[endpos][item]  # letzter Tochterknoten
        splitpos = child[-1]  # Startposition des letzten Tochterknotens
        if dotpos > 1:
            # vorherige Tochterknoten ausgeben
            self.print_children((lhs, rhs, dotpos - 1, startpos), splitpos)
        # letzten Tochterknoten ausgeben
        self.print_parse(child, endpos)

    def print_parse(self, item, endpos):

        lhs, rhs, dotpos, startpos = item
        # Kategorie der Konstituente ausgeben
        print('(' + lhs, end=' ')
        if self.childitem[endpos][item] is None:
            # terminalen Tochterknoten ausgeben
            print(rhs[0], end='')
        else:
            # Liste von nichtterminalen Tochterknoten ausgeben
            self.print_children(item, endpos)
        print(')', end='')  # schließende Klammer

    def parse(self, tokens):
        self.logvitp = [{} for _ in range(len(tokens) + 1)]
        self.childitem = [{} for _ in range(len(tokens) + 1)]
        for i in range(len(tokens)):
            self.scan(tokens[i], i)

        bestscore, bestitem = -1e300, None
        for item, score in self.logvitp[-1].items():
            lhs, rhs, dotpos, startpos = item

            if lhs == 'S' and dotpos == len(rhs) and startpos == 0:

                if bestscore < score:
                    bestscore = score
                    bestitem = item
        if bestitem is None:
            print('no analysis for:', ' '.join(tokens))
        else:
            self.print_parse(bestitem, len(tokens))
            print('')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: parser.py grammar lexicon textfile")
    parser = Parser(sys.argv[1], sys.argv[2])

    # Eingabesätze einlesen
    with open(sys.argv[3]) as file:
        for line in file:
            tokens = line.split()
            if len(tokens) > 0:
                parser.parse(tokens)