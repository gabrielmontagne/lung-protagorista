#!/usr/bin/env python3

import sys
import re

section_marker = re.compile(r'\s*###\s*(.*)')
header_marker = re.compile(r'\s*#')


class Sections:

    def __init__(self):
        self.lines = []
        self.paragraphs = []
        self.sections = []

    def addlines(self, filename, lines):
        self.lines.extend(lines)

        section = None
        paragraph = None

        linenumber = 0
        for l in lines:

            linenumber += 1
            is_space = l.isspace()
            is_section_marker = section_marker.match(l)
            is_header_marker = header_marker.match(l)

            if section_marker.match(l) or not section and not is_space:
                if section:
                    self.sections.append(section)

                section = Part(filename, linenumber)

            if section:
                if is_section_marker:
                    section.addHeader(l)
                elif not is_header_marker:
                    section.addline(l.rstrip())

            if not paragraph and not is_space and not is_header_marker:
                paragraph = Part(filename, linenumber)

            if paragraph:
                if not is_space and not is_header_marker:
                    paragraph.addline(l.rstrip())
                else:
                    self.paragraphs.append(paragraph)
                    paragraph = None

        if paragraph:
            self.paragraphs.append(paragraph)

        if section:
            self.sections.append(section)


class Part:

    def __init__(self, filename, linenumber):
        self.filename = filename
        self.linenumber = linenumber
        self.lines = []
        self.head = ""

    def addline(self, line):
        self.lines.append(line)

    def addHeader(self, line):
        if not self.head:
            self.head = re.sub(section_marker, r"\1", line)

    def body(self):
        return "".join(self.lines)

    def __repr__(self):
        return ";".join(["Part", str(self.filename), str(self.linenumber)])


def main():
    files = sys.argv[1:]
    s = Sections()

    for filename in files:
        with open(filename) as f:
            s.addlines(f.name, f.readlines())

    for p in s.sections:
        print("\n----- S →", p.head)
        print(p.body())

if __name__ == "__main__":
    main()
