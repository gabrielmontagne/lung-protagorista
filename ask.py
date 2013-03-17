#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tempfile
import difflib
import os
import subprocess

STOP = "@@ stop @@"
SEPARATOR = "@@ ============"
VIM_FT = "@@ vim:ft=diff"

class Asker:
    def __init__(self):
        self.differ = difflib.Differ()

    def ask(self, question, hint=""):

        question_lines = ["", "", STOP]

        if "n" in question:
          question_lines.append("## %(n)s:%(ln)s" % question)

        question_lines.extend([SEPARATOR, ""])
        question_lines.extend(question['q'])
        question_lines.extend(["", SEPARATOR])

        if hint:
            question_lines.extend(["", "", hint, ""])

        question_lines.append(VIM_FT)

        prompt = "\n".join(question_lines)

        input_lines = self.bleach_lines(self.input_editor(prompt).split("\n"))

        if len(input_lines):
            if input_lines[0] == ':quit':
                sys.exit(0)
            if input_lines[0] == ':skip':
                raise QuestionAbort('aborting')
            if input_lines[0] == ':reload':
                raise AbortAndReload('aborting')

        answer_lines = self.bleach_lines(question['a'])
        if input_lines == answer_lines:
            return ""

        return "\n".join(self.differ.compare(input_lines, answer_lines))


    def bleach_lines(self, lines):
        """Return only non-empty lines, non-commented out lines."""
        if STOP in lines:
            lines = lines[:lines.index(STOP)]

        return  [line.rstrip() for line in lines if re.search('\S', line) and
            re.search('^[^%]', line)]

    def input_editor(self, prompt=' '):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(prompt)
        f.close()
        call = subprocess.call(["vim", f.name])
        f = open(f.name)
        results = f.read()
        os.unlink(f.name)
        return results

class QuestionAbort(Exception):
    pass

class AbortAndReload(Exception):
    pass
