from .ask import Asker, QuestionAbort, AnswerShow, AbortAndReload, Quit
from .lines import lines
from .weightedrandom import WeightedRandom
from functools import reduce
from hashlib import md5
from itertools import groupby
from math import inf
import imp
import logging
import os
import re
import shelve
import sys

weights_file = os.path.expanduser("~/.lung/weights")
min_factor = 0.2
max_factor = 20
factor_on_correct = 0.7
factor_on_wrong = 1.2
factor_on_wrong_with_hint = 1.2
dynamic_module_count = 0

break_prefixes = ('%__ END __', '<!-- END -->', '<!-- SOURCE -->', '----', '#__ END __', '//__ END __')

comment_prefixes = ('#', '//')
comment_prefixes_list_ext = ('<<', '@@', '{{', '[x]')
initial_factor_extract = re.compile(r'\^\[W:(\d+\.\d+)\]', re.I)

log = logging.getLogger(__name__)


def is_comment(line):
    return line[1].lstrip().startswith(comment_prefixes)


def remove_comment(line):
    for prefix in comment_prefixes:
        line = re.sub(prefix, '', line)

    return line


def initial_factor_from(line):
    weight = initial_factor_extract.match(line)
    if not weight:
        return None

    return float(weight.groups()[0])


def remove_outer_indent(lines):
    min_indent = reduce(
        lambda x, y: min(x, len(y) - len(y.lstrip())),
        lines,
        inf
    )

    return [l[min_indent:] for l in lines]


class Quiz:

    asker = Asker()

    def __init__(self, configuration):

        log.debug('quiz init')

        self.configuration = configuration
        self.current_q_index = None
        self.create_questions()

    def create_questions(self):

        global dynamic_module_count

        configuration = self.configuration

        def grep(e):
            if not configuration.g:
                return True
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

        if configuration.cc:
            for cc in configuration.cc:
                p = PerCommentsParser(lines(cc), cc)
                q.extend(filter(grep, p.get_questions()))

        if configuration.m:
            for m in configuration.m:
                if m.startswith(('.', '/')):
                    module = imp.load_source(
                        'dyn' + str(dynamic_module_count), m)
                    dynamic_module_count += 1
                else:
                    import importlib
                    module = importlib.import_module(m)

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
            index = min(self.current_q_index, len(self.questions) - 1)
            question = self.questions[index]
            question_id = self.hash_for_question(question)
            self.sequential_index = index + 1

        elif self.sequential_run:
            question = self.questions[
                self.sequential_index % len(self.questions)]
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
            question_weights.sync()

        while True:
            try:
                question['weight'] = weight
                hint = self.asker.ask(question, hint)
                first_run = question.get('first_run', False)

                if hint:

                    if first_run:
                        log.debug(
                            'wrong answer on first run -- present with hint')
                    else:
                        log.debug('wrong answer -- present with hint')

                    if not self.lock_weights and not first_run:
                        if previous_hint:
                            weight *= factor_on_wrong_with_hint
                        else:
                            weight *= factor_on_wrong

                    streak = 0
                    previous_hint = hint
                    record_weight()
                    continue

                question['first_run'] = False

                if not previous_hint:
                    if not self.lock_weights:
                        weight *= factor_on_correct

                    record_weight()
                    break

                streak += 1
                if streak > self.correct_in_row:
                    break

            except AnswerShow:
                question['first_run'] = False
                hint = '\n'.join(question['a'])
                streak = 0

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

        question_weights = shelve.open(weights_file)

        for q in self.questions:
            question_id = self.hash_for_question(q)
            if not question_id in question_weights:
                log.debug("initialize factor for q: " + question_id[:5] + "\n")

                if 'initial-factor' in q:
                    question_weights[question_id] = q['initial-factor']

                else:
                    log.debug('First run for question {}'.format(
                        question_id[:5]))
                    question_weights[question_id] = 1
                    q['first_run'] = True


                question_weights.sync()

            else:
                log.debug(question_id[:5] + ", factor: " +
                          str(question_weights[question_id]) + "\n")

            question_by_id[question_id] = q
            questions_for_random[question_id] = question_weights[question_id]

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
            line_number += 1
            clean_line = re.sub(r'^\[ \]\s*\d*\s+', '', line)

            if len(line.strip()) == 0:
                continue

            if line.startswith(break_prefixes):
                break

            if line.startswith(comment_prefixes):
                continue

            if line.startswith(comment_prefixes_list_ext):
                continue

            # Split the line using '|'
            parts = clean_line.split('|', 1)
            question_text = parts[0].strip()
            answer_text = parts[1].strip() if len(parts) > 1 else 'ok'

            current_item = {'q': [question_text], 'a': [answer_text], 'ln': line_number}

            weight_factor = initial_factor_from(question_text)
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


class PerCommentsParser:

    def __init__(self, lines, name):

        questions = []
        q = None

        for chunk in groupby(enumerate(lines), is_comment):
            if chunk[0]:
                q_lines = list(chunk[1])
                q = {
                    'q': remove_outer_indent([remove_comment(c[1]).rstrip() for c in q_lines]),
                    'ln': q_lines[0][0] + 1,
                }
                if name:
                    q['n'] = name

            else:
                if not q:
                    q = {
                        'q': ['Preamble'],
                        'ln': 1
                    }

                    if name:
                        q['n'] = name

                q['a'] = remove_outer_indent(
                    [a[1].rstrip() for a in chunk[1] if a[1].strip()])

                questions.append(q)
                q = None

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
            line_number += 1
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
                    current_item = None

                if current_item == None:

                    current_item = {
                        'q': [line.strip()], 'a': [], 'ln': line_number}

                    weight_factor = initial_factor_from(line)
                    if weight_factor:
                        current_item['initial-factor'] = weight_factor

                    if name:
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
            answer = answer.rstrip()

            current_item['a'].append(answer)

        if current_item and len(current_item['a']) > 0:
            questions.append(current_item)

        self.questions = questions
        return questions

    def get_questions(self):
        return self.questions
