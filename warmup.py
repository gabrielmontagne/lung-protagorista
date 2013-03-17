#!/usr/bin/env python
# -*- coding: utf-8 -*-

import q
import os
import weighted_random


def main():
    wr = weighted_random.WeightedRandom(
      {
        "aaaa": 2
      , "bbbb": 3
      , "cccc": 1
      }
    )

    for x in range(10):
        print(wr.random())

    wr.adjust_weight("eee", 2)
    print("---")

    for x in range(10):
        print(wr.random())


if __name__ == "__main__": 
    main()
