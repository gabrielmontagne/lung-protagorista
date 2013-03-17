#!/usr/bin/env python
# -*- coding: utf-8 -*-

STOP = "@@ stop @@"
SEPARATOR = "@@ ============"

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

        print("line_info", prompt)

        return "hh"

class QuestionAbort(Exception):
    pass

class AbortAndReload(Exception):
    pass
