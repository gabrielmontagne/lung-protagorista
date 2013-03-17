#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import re
import os
import shelve
import md5
import weighted_random

class Quiz:
    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-f', nargs='+', type=file, required=True)
        parser.add_argument('-m', nargs='+', type=str, required=True)
        configuration = parser.parse_args()

        q = []

        for f in configuration.f:
            p = LungParser(f)
            q.extend(p.get_questions())

        for m in configuration.m:
            module = __import__(m)
            q.extend(module.get_questions())

        self.questions = q

        self.weight_questions()

    def ask(self):
        pass

    def weight_questions(self):

        config_path = os.path.expanduser("~/.lung")
        weights_file = os.path.expanduser("~/.lung/weights.db")

        # create home folder if not existing
        if not os.access(config_path, os.F_OK): 
            os.mkdir(config_path)

        # open hash cache
        cache = shelve.open(weights_file)
        print("cache", cache)

        for q in self.questions:

            question_hash = self.hash_for_question(q)

            if not question_hash in cache:
                print("initialize factor for q.", question_hash)
                cache[question_hash] = 1
            else:
                print(question_hash, "factor", cache[question_hash])

            weight = cache[question_hash]

        cache.close()

    def hash_for_question(self, q):
        return md5.new("\n".join(q['q'])).hexdigest()
        

class LungParser:

    def __init__(self, lung_file):
        self.dictify(lung_file)

    def dictify(self, lung_file):
        print("dictify", lung_file)
        questions = []
        current_item = None
        line_number = 0
        for line in lung_file:
            line_number = line_number + 1
            if len(line.strip()) == 0:
                continue

            if re.search(r'^%__ END __', line):
                break

            if re.search(r'^----', line):
                break

            if re.search(r'^%', line):
                if current_item and len(current_item['a']):
                    questions.append(current_item)

                current_item = None
                continue

            if re.search("^\S", line):
                if current_item and len(current_item['a']):
                    questions.append(current_item)
                    current_item = None;

                if current_item == None:
                    current_item = {'q': [line.strip()], 'a': [], 'ln': line_number}
                    try:
                        current_item['n'] = lung_file.name
                    except AttributeError:
                        print "Input doesn't have a name."
                else:
                    current_item['q'].append(line.strip())

                continue

            if not current_item:
                continue

            answer = re.sub(r"^( ){,4}",  "",  line)
            answer = re.sub(r"#%.*", "", answer)
            answer = re.sub(r"//%.*", "", answer)
            answer = answer.rstrip();

            current_item['a'].append(answer)

        if current_item and len(current_item['a']) > 0:
            questions.append(current_item)

        self.questions = questions
        return questions


    def get_questions(self):
        return self.questions
