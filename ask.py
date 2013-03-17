#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tempfile
import os
import subprocess

STOP = "@@ stop @@"
SEPARATOR = "@@ ============"
VIM_FT = "@@ vim:ft=diff"

class Asker:
    def ask(self, question, hint = ''):

        if "n" in question:
            line_info = "## %(n)s:%(ln)s" % question
        else: 
            line_info = ""

        question_lines = [STOP, line_info, SEPARATOR, ""]
        question_lines.extend(question['q'])
        question_lines.extend(["", SEPARATOR])

        prompt = "\n\n" +  "\n".join(question_lines)

        if hint:
            prompt += "\n\n" + hint + "\n"

        prompt +=  "\n" + VIM_FT

        input_lines = self.bleach_lines(self.input_editor(prompt).split("\n"))


        print("results", input_lines)

        return "hh"

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
