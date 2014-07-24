#!/usr/bin/env python3

import os

source = "~/.t/x.md"
notes = 3
items = []

with open(os.path.expanduser(source)) as f:
    items = f.readlines()

def get_questions():
    result = []
    for x in range(min(len(items), notes)):
        result.append(
          {
            'q': [ items[x].strip() ]
          , 'a': [ "ok" ]
          }
        )

    return result
