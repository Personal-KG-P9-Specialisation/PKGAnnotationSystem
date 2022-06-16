import json
from collections import Counter

def histogram(path):
    rels = load_rels(path)
    counted_rels = Counter(rels)
    print(counted_rels)


def load_rels(path):
    f = open(path,'r')
    rels = []
    for l in f:
        conv = json.loads(l)
        for rel in conv['relations']:
            rels.append(rel['label'])
    f.close()
    return rels