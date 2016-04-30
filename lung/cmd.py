import cmd
import re
import os

# from .ask import Asker


print('ok')

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

