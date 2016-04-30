from .ask import Asker, QuestionAbort, AbortAndReload, Quit
from .q import Quiz
import cmd
import os
import re


class LungCMD(cmd.Cmd):
    """CLI for lung"""

    prompt = 'lung> '

    def __init__(self, single_answer=False, intro=None):
        self.single_answer = single_answer
        self.result = []
        super().__init__(intro)

    def do___quit(self, *args):
        raise Quit

    def do___skip(self, *args):
        raise QuestionAbort

    def do___reload(self, *args):
        raise AbortAndReload

    def do_EOF(self, *args):
        return True

    def default(self, line):
        self.result.append(line)
        return self.single_answer

    def emptyline(self):
        return True

    def precmd(self, line):
        return line.replace(':', '__')


class CMDAsker(Asker):

    def ask(self, question, hint=''):

        os.system('clear')

        if hint:
            print('>' * 10)
            print(hint)
            print('<' * 10)

        command = LungCMD(len(question['a']) == 1)
        command.cmdloop(
            '\n'.join(self.preprocess_question_lines(question['q'])))

        answer_lines = self.bleach_lines(question['a'])
        input_lines = self.bleach_lines(command.result)

        if input_lines == answer_lines:
            return ''

        return '\n'.join(self.differ.compare(input_lines, answer_lines))


class CMDQuiz(Quiz):

    asker = CMDAsker()
