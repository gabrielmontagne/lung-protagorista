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

        print("line_info", line_info)

        return "hh"

class QuestionAbort(Exception):
    pass

class AbortAndReload(Exception):
    pass
