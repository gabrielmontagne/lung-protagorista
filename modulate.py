#!/usr/bin/env python3

import glob
import os
import parse
import random

s = parse.Sections()
notes = 300

instructions = []

for f in glob.glob(os.path.expanduser("~/.modulations/*.txt")):
    with open(f) as i:
        instructions.extend(["@@ " + l for l in i])

for f in glob.glob(os.path.expanduser("~/.modulations/*.md")):
    with open(f) as i:
        s.addlines(i.name, i.readlines())

def get_questions():
    result = []
    for p in random.sample(s.paragraphs, min(len(s.paragraphs), notes)):
        q = random.sample(instructions, 1) 
        q.extend(p.lines)
        q.extend([ "", "@@ context: %s" % p.filename + ":" + str(p.linenumber)])
        result.append(
          {
            'q': q
          , 'a' : [ "ok" ]
          }
        )

    return result

if __name__ == "__main__":
    print("\n".join(map(str, (get_questions()))))
