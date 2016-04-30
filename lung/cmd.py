from .ask import Asker
from .q import Quiz
import cmd
import os
import re

print('ok')

class CMDAsker(Asker):
    def ask(self, question, hint=''):

        print('ask question', question, hint)

        r = input('tons> ')

        answer_lines = self.bleach_lines(question['a'])
        input_lines = self.bleach_lines([ r ])


        if input_lines == answer_lines:
            return ''

        return '\n'.join(self.differ.compare(input_lines, answer_lines))

class CMDQuiz(Quiz):

    asker = CMDAsker()

    def __init__(self, configuration):
        print('un CMD Quizzu', configuration)
        super().__init__(configuration)

class LungCMD(cmd.Cmd):

    prompt = 'oksカか> '

    def do_read(self, *args):
        print('Read!', args)

    def do___read(self, *args):
        print('the other read', args)

    def do_EOF(self, *args):
        print(chr(27) + '[2J')

    def default(self, line):
        print('default', line)

    def precmd(self, line):
        return line.replace(':', '_')
