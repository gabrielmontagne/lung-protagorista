
from .ask import Asker, QuestionAbort, AbortAndReload, Quit
from .lines import lines
from .weightedrandom import WeightedRandom 
from hashlib import md5
import imp
import os
import re
import shelve
import sys
import time

config_path = os.path.expanduser("~/.lung")
weights_file = os.path.expanduser("~/.lung/weights")
log_file = os.path.expanduser("~/.lung/run.log")
min_factor = 0.1
max_factor = 100
factor_on_correct = 0.5
factor_on_wrong = 1.7
factor_on_wrong_with_hint = 1.4
dynamic_module_count = 0
break_prefixes = (
  '%__ END __'
, '<!-- END -->'
, '<!-- SOURCE -->'
, '----'
)

initial_factor_extract = re.compile(r'\^\[W:(\d+\.\d+)\]', re.I)

def initial_factor_from(line):
    weight = initial_factor_extract.match(line)
    if not weight:
        return None

    return float(weight.groups()[0])

class Quiz:

    asker = Asker()

    def __init__(self, configuration):

        self.configuration = configuration
        self.current_q_index = None
        self.create_questions()

    def create_questions(self):
        global dynamic_module_count

        configuration = self.configuration

        def grep(e):
            if not configuration.g: return True
            return any(
                pattern in line
                for pattern in configuration.g
                for line in e['q']
            )

        q = []

        if configuration.f:
            for f in configuration.f:
                p = LungParser(lines(f), f)
                q.extend(filter(grep, p.get_questions()))

        if configuration.m:
            for m in configuration.m:
                if m.startswith(('.', '/')):
                    module = imp.load_source(
                        'dyn' + str(dynamic_module_count), m)
                    dynamic_module_count += 1
                else:
                    module = __import__(m)

                q.extend(filter(grep, module.get_questions()))

        if configuration.l:
            for l in configuration.l:
                l = ListParser(lines(l), l)
                q.extend(filter(grep, l.get_questions()))

        if not len(q):
            raise Exception("No questions extracted, specify -f, -m or -l")

        self.questions = q
        self.weightedrandom = WeightedRandom({})
        self.weight_questions()
        self.sequential_index = 0
        self.sequential_run = configuration.s
        self.correct_in_row = configuration.c
        self.lock_weights = configuration.lw

    def ask(self):

        if self.current_q_index is not None:
            index = min(self.current_q_index, len(self.questions) -1 )
            question = self.questions[ index ]
            question_id = self.hash_for_question(question)
            self.sequential_index = index + 1
        elif self.sequential_run:
            question = self.questions[self.sequential_index % len(self.questions)]
            question_id = self.hash_for_question(question)
            self.sequential_index += 1
        else:
            question_id = self.weightedrandom.random()
            question = self.question_by_id[question_id]

        self.current_q_index = None
        question_weights = shelve.open(weights_file)

        weight = question_weights[question_id]
        streak = 0
        previous_hint = None
        hint = ''

        def record_weight():
            question_weights[question_id] = max(
                    min(weight, max_factor), min_factor)

        while True:
            try:
                question['weight'] = weight
                hint = self.asker.ask(question, hint)

                if hint:
                    if not self.lock_weights:
                            if previous_hint: weight *= factor_on_wrong_with_hint
                            else: weight *= factor_on_wrong

                    streak = 0
                    previous_hint = hint
                    record_weight()
                    continue

                if not previous_hint:
                    if not self.lock_weights:
                            weight *= factor_on_correct

                    record_weight()
                    break

                streak += 1
                if streak > self.correct_in_row: break

            except QuestionAbort:
                return

            except AbortAndReload:
                question_weights.close()
                self.current_q_index = self.questions.index(question)
                self.create_questions()
                return

            except Quit:
                print('...ciao')
                sys.exit(0)

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

                if 'initial-factor' in q:
                    question_weights[question_id] = q['initial-factor']
                else:
                    question_weights[question_id] = 1

            else:
                log.write(question_id + ", factor: " + str(question_weights[question_id]) + "\n")

            question_by_id[question_id] = q
            questions_for_random[question_id] = question_weights[question_id]

        log.close()

        self.question_by_id = question_by_id
        self.weightedrandom.set_weights(questions_for_random)
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
            clean_line = re.sub('^\d+\.\s+', '', line)

            if len(line.strip()) == 0:
                continue

            if line.startswith(break_prefixes):
                break

            if re.search(r'^x ', line):
                continue

            if re.search(r'^#', line):
                continue

            current_item = { 'q': [ clean_line ] , 'a': [ 'ok' ], 'ln': line_number }

            weight_factor = initial_factor_from(clean_line)
            if weight_factor is not None:
                current_item['initial-factor'] = weight_factor

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

            if line.startswith(break_prefixes):
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

                    weight_factor = initial_factor_from(line)
                    if weight_factor is not None:
                        current_item['initial-factor'] = weight_factor

                    if name is not None:
                        current_item['n'] = name
                    else:
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
