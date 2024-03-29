import cmd
import difflib
import os
import re
import subprocess
import tempfile

STOP = "@@ stop @@"
SEPARATOR = "@@ ============"
VIM_FT = "@@ vim:ft=diff:fo="


class Asker:

    differ = difflib.Differ()

    def ask(self, question, hint=""):

        question_lines = ["", "", STOP]

        if 'n' in question:
            question_lines.append('## %(n)s:%(ln)s' % question)

        if 'weight' in question:
            question_lines.append('@@ W:%(weight).3f' % question)

        question_lines.extend([SEPARATOR, ''])

        processed_lines = self.preprocess_question_lines(question['q'])

        question_lines.extend(processed_lines)
        question_lines.extend(['', SEPARATOR])

        if hint:
            question_lines.extend(["", "", hint, ""])

        question_lines.append(VIM_FT)

        prompt = '\n'.join(question_lines)

        input_lines = self.bleach_lines(self.input_editor(prompt).split('\n'))

        if len(input_lines):
            if input_lines[0] == ':quit':
                raise Quit('quitting')
            if input_lines[0] == ':skip':
                raise QuestionAbort('aborting')
            if input_lines[0] == ':show':
                raise AnswerShow('show and continue')
            if input_lines[0] == ':reload':
                raise AbortAndReload('aborting')
            if input_lines[0] == ':ok':
                return ""

        answer_lines = self.bleach_lines(question['a'])

        if input_lines == answer_lines:
            return ""

        return "\n".join(self.differ.compare(input_lines, answer_lines))

    def preprocess_question_lines(self, lines):

        question_lines = []

        execute_match = re.match('^ex:(.*)', lines[0])
        if execute_match:
            os.system(execute_match.groups()[0])
            question_lines.extend(lines[1:])
        else:
            question_lines.extend(lines)

        return question_lines

    def bleach_lines(self, lines):
        """Return only non-empty lines, non-commented out lines."""
        if STOP in lines:
            lines = lines[:lines.index(STOP)]

        return [line.rstrip() for line in lines if re.search('\S', line)]

    def input_editor(self, prompt=' '):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(prompt.encode('utf-8'))
        f.close()
        call = subprocess.call(["vim", f.name])
        f = open(f.name)
        results = f.read()
        os.unlink(f.name)
        return results

class AnswerShow(Exception):
    pass

class QuestionAbort(Exception):
    pass


class AbortAndReload(Exception):
    pass


class Quit(Exception):
    pass
