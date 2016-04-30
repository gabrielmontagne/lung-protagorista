from .ask import Asker
from .q import Quiz
import cmd
import os
import re

print('ok')

class LungCMD(cmd.Cmd):

    prompt = 'lung> '

    def __init__(self, single_answer=False, intro=None):
        self.single_answer = single_answer
        self.result = []
        super().__init__(intro)

    def do___quit(self, *args):
        print('the QUIT', args)

    def do_EOF(self, *args):
        return True

    def default(self, line):
        self.result.append(line)
        return self.single_answer

    def precmd(self, line):
        return line.replace(':', '__')

class CMDAsker(Asker):
    def ask(self, question, hint=''):

        if hint:
            print('>' * 10)
            print(hint)
            print('<' * 10)

        command = LungCMD(len(question['a']) == 1)
        command.cmdloop('\n'.join(question['q']))

        answer_lines = self.bleach_lines(question['a'])
        input_lines = self.bleach_lines(command.result)

        print('input', input_lines)

        if input_lines == answer_lines:
            return ''

        return '\n'.join(self.differ.compare(input_lines, answer_lines))

class CMDQuiz(Quiz):

    asker = CMDAsker()
