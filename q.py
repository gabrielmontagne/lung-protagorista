#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import re
import os
import shelve
import md5
import weighted_random
import ask

config_path = os.path.expanduser("~/.lung")
weights_file = os.path.expanduser("~/.lung/weights.db")
min_factor = 0.1
max_factor = 10
factor_on_correct = 0.5
factor_on_wrong = 1.5
factor_on_wrong_with_hint = 1.3
correct_without_hint = 3

class Quiz:
    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-f', nargs='+', type=file, required=False)
        parser.add_argument('-m', nargs='+', type=str, required=False)
        configuration = parser.parse_args()

        q = []

        print(configuration)

        if configuration.f:
            for f in configuration.f:
                p = LungParser(f)
                q.extend(p.get_questions())

        if configuration.m:
            for m in configuration.m:
                module = __import__(m)
                q.extend(module.get_questions())

        self.questions = q
        self.weighted_random = weighted_random.WeightedRandom({})
        self.weight_questions()
        self.asker = ask.Asker()

    def ask(self):

        question_id = self.weighted_random.random()
        question = self.question_by_id[question_id]
        question_weights = shelve.open(weights_file)
        hint = self.asker.ask(question)
        weight = question_weights[question_id] 

        if not hint:
            weight *= factor_on_correct
        else:
            weight *= factor_on_wrong
            streak = 0
            while hint or streak < correct_without_hint:
                hint = self.asker.ask(question, hint)
                if hint:
                    weight *= factor_on_wrong_with_hint
                    streak = 0
                    raw_input("0")
                else: 
                    streak += 1
                    print("s " + str(streak))
                    print(streak < correct_without_hint)
                    raw_input("+1")

        question_weights[question_id] = max(min(weight, max_factor), min_factor)
        question_weights.close()
        self.weight_questions()

    def weight_questions(self):

        question_by_id = {}
        questions_for_random = {}

        if not os.access(config_path, os.F_OK): 
            os.mkdir(config_path)

        question_weights = shelve.open(weights_file)

        for q in self.questions:
            question_id = self.hash_for_question(q)
            if not question_id in question_weights:
                print("initialize factor for q.", question_id)
                question_weights[question_id] = 1
            else:
                print(question_id, "factor", question_weights[question_id])

            question_by_id[question_id] = q
            questions_for_random[question_id] = question_weights[question_id]

        print("\nWeights:")
        print(questions_for_random)
        raw_input("\nQuestions ready....")
        self.question_by_id = question_by_id
        self.weighted_random.set_weights(questions_for_random)

        question_weights.close()

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
