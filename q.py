#!/usr/bin/env python3

from hashlib import md5
import argparse
import ask
import imp
import lines
import os
import re
import shelve
import time
import weighted_random

config_path = os.path.expanduser("~/.lung")
weights_file = os.path.expanduser("~/.lung/weights")
log_file = os.path.expanduser("~/.lung/run.log")
min_factor = 0.1
max_factor = 100
factor_on_correct = 0.5
factor_on_wrong = 1.7
factor_on_wrong_with_hint = 1.4
dynamic_module_count = 0

class Quiz:
    def __init__(self):

        self.current_q_index = None
        self.create_questions()

    def create_questions(self):
        global dynamic_module_count

        parser = argparse.ArgumentParser()
        parser.add_argument("-s", action='store_true', help='sequential (non random)', required=False )
        parser.add_argument('-f', nargs='+', required=False, help='files')
        parser.add_argument('-l', nargs='+', required=False, help='lists')
        parser.add_argument('-m', nargs='+', type=str, required=False, help='modules')
        parser.add_argument('-c', nargs='?', type=int, default=3, required=False, help='corret retries')
        configuration = parser.parse_args()

        q = []

        if configuration.f:
            for f in configuration.f:
                p = LungParser(lines.lines(f), f)
                q.extend(p.get_questions())

        if configuration.m:
            for m in configuration.m:
                if m.startswith(('.', '/')):
                    module = imp.load_source(
                        'dyn' + str(dynamic_module_count), m)
                    dynamic_module_count += 1
                else:
                    module = __import__(m)

                q.extend(module.get_questions())

        if configuration.l:
            for l in configuration.l:
                l = ListParser(lines.lines(l), l)
                q.extend(l.get_questions())

        if not len(q):
            raise Exception("No questions extracted, specify -f, -m or -l")

        self.questions = q
        self.weighted_random = weighted_random.WeightedRandom({})
        self.weight_questions()
        self.asker = ask.Asker()
        self.sequential_index = 0
        self.sequential_run = configuration.s
        self.correct_in_row = configuration.c

    def ask(self):

        if self.current_q_index is not None:
            question = self.questions[self.current_q_index]
            question_id = self.hash_for_question(question)
        elif self.sequential_run:
            question = self.questions[self.sequential_index % len(self.questions)]
            question_id = self.hash_for_question(question)
            self.sequential_index += 1
        else:
            question_id = self.weighted_random.random()
            question = self.question_by_id[question_id]

        self.current_q_index = None

        question['weight'] = self.weighted_random.get_weight(question_id)

        try:
            hint = self.asker.ask(question)
        except ask.QuestionAbort:
            return
        except ask.AbortAndReload:
            self.current_q_index = self.questions.index(question)
            self.create_questions()
            return

        question_weights = shelve.open(weights_file)
        weight = question_weights[question_id]

        if not hint:
            weight *= factor_on_correct
        else:
            weight *= factor_on_wrong
            streak = 0
            while hint or streak < self.correct_in_row:
                try:
                    question['weight'] = weight
                    hint = self.asker.ask(question, hint)
                except ask.QuestionAbort:
                    return
                except ask.AbortAndReload:
                    self.current_q_index = self.questions.index(question)
                    self.create_questions()
                    return

                if hint:
                    weight *= factor_on_wrong_with_hint
                    streak = 0
                else:
                    streak += 1


        question_weights[question_id] = max(min(weight, max_factor), min_factor)
        question_weights.close()
        self.weight_questions()

    def weight_questions(self):

        question_by_id = {}
        questions_for_random = {}

        if not os.access(config_path, os.F_OK):
            os.mkdir(config_path)

        log = open(log_file, "a")
        log.write("\nweigh questions\n")

        question_weights = shelve.open(weights_file)

        for q in self.questions:
            question_id = self.hash_for_question(q)
            if not question_id in question_weights:
                log.write("initialize factor for q: " + question_id + "\n")
                question_weights[question_id] = 1
            else:
                log.write(question_id + ", factor: " + str(question_weights[question_id]) + "\n")

            question_by_id[question_id] = q
            questions_for_random[question_id] = question_weights[question_id]

        log.close()

        self.question_by_id = question_by_id
        self.weighted_random.set_weights(questions_for_random)
        question_weights.close()

    def hash_for_question(self, q):
        return md5(("\n".join(q['q'])).encode()).hexdigest()

class ListParser:
    def __init__(self, lines, name):
        self.dictify(lines, name)

    def dictify(self, lines, name):
        questions = []
        line_number = 0
        for line in lines:
            line_number = line_number + 1
            if len(line.strip()) == 0:
                continue

            if re.search(r'^%__ END __', line):
                break

            if re.search(r'^<!-- END -->', line):
                break

            if re.search(r'^<hr', line):
                break

            if re.search(r'^----', line):
                break

            if re.search(r'^x ', line):
                continue

            if re.search(r'^#', line):
                continue

            current_item = { 'q': [ re.sub('^\d+\.\s+', '', line) ] , 'a': [ 'ok' ], 'ln': line_number }

            try:
                current_item['n'] = name
            except AttributeError:
                print("Input doesn't have a name.")

            questions.append(current_item)

        self.questions = questions

    def get_questions(self):
        return self.questions


class LungParser:

    def __init__(self, lines, name):
        self.dictify(lines, name)

    def dictify(self, lines, name):
        questions = []
        current_item = None
        line_number = 0
        for line in lines:
            line_number +=  1
            if len(line.strip()) == 0:
                continue

            if re.search(r'^%__ END __', line):
                break

            if re.search(r'^<!-- END -->', line):
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
                        current_item['n'] = name
                    except AttributeError:
                        print("Input doesn't have a name.")
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
