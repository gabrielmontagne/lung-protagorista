#!/usr/bin/env python3
import sys
import os
from lung.q import ListParser

def get_questions():
    files = [f for f in sys.argv[1:]
             if os.path.isfile(f)]
    if not files:
        raise Exception("ranked.py needs one or more input files as arguments")
    questions = []
    for fn in files:
        with open(fn, encoding='utf-8') as fp:
            lines = fp.read().splitlines()
        parser = ListParser(lines, fn)
        questions.extend(parser.get_questions())

    total = len(questions)
    Wmax, Wmin = 2.0, 0.7
    for idx, q in enumerate(questions, start=1):
        if total > 1:
            q['initial-factor'] = Wmax - (idx - 1) * (Wmax - Wmin) / (total - 1)
        else:
            q['initial-factor'] = Wmax
    return questions
