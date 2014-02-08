#!/usr/bin/env python3

import q
import os
import weighted_random
import time


def main():
    quiz = q.Quiz()
    for x in range(200):
        quiz.ask()

if __name__ == "__main__": 
    main()
