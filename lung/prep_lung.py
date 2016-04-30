#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes a file with the paths for all the files to process.
It will generate a result.md lung file, where the path is the key and the
content is the answer.
"""

import sys


def process_file(path):
    print "process %s" % path
    try:
        index = open(path)
        output = open("result.md", "w")
        for entry in index:
            try:
                quiz = open(entry.rstrip())
                output.write("\n\n%s \n\n" % entry.rstrip())
                for line in quiz:
                    output.write("    %s\n" % line.rstrip())
                quiz.close()
            except:
                print "couldn't open quiz entry '%s'." % quiz
        output.close()
    except:
        print "couldn't process %s." % path


def main():
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print "usage: prep_lung.py index"

if __name__ == "__main__":
    main()
