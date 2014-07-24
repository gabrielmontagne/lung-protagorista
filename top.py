#!/usr/bin/env python3

import os

source = "~/.t/a.md"
notes = 20
items = []

with open(os.path.expanduser(source)) as f:
    items = f.readlines()

def get_questions():
    result = []
    for x in range(min(len(items), notes)):
        q = [ items[x].strip() ]
        q.extend([ "", "@@ context %s" % source + ":" + str(x) ])
        result.append({ 'q': q , 'a': [ "ok" ] })

    return result
