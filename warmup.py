#!/usr/bin/env python
# -*- coding: utf-8 -*-

import q
import os
import weighted_random


def main():
    quiz = q.Quiz()
    for x in range(10):
      quiz.ask()


if __name__ == "__main__": 
    main()
