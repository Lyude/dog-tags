#!/usr/bin/python3
import re
import os
from glob import iglob

class KeywordHighlight():
    def __init__(self, name, highlight_group, preceding_keyword=None):
        self.global_tags = set()
        self.local_tags = dict()

        self.name = name
        self.highlight_group = highlight_group
        self.preceding_keyword = preceding_keyword

    def add_tag(self, tag, scope=None):
        if scope != None:
            if scope not in self.local_tags:
                self.local_tags[scope] = set()

            dest = self.local_tags[scope]
        else:
            dest = self.global_tags

        dest.add(tag.tag_name)

    def generate_script(self, out):
        def print_keyword_highlight(keywords):
            out.write("syn keyword %s %s" % (self.name, " ".join(keywords)))

            if self.preceding_keyword != None:
                out.write(" containedin=%sPreceding\n" % self.name)
            else:
                out.write("\n")

        if self.preceding_keyword != None:
            out.write("syn match %sPreceding \"\(%s\s\)\@<=\S\+\" contains=%s transparent\n" % \
                      (self.name, self.preceding_keyword, self.name))

        if len(self.global_tags) != 0:
            print_keyword_highlight(self.global_tags)

        first_conditional_printed = False
        for scope in self.local_tags.keys():
            if first_conditional_printed:
                out.write("else")
            else:
                first_conditional_printed = True

            # Compare against the full path if the tag paths are
            # absolute
            if scope.startswith("/"):
                out.write("if expand('%%:p') == '%s'\n" % scope)
            else:
                out.write("if @%% == '%s'\n" % scope)

            out.write("\t")
            print_keyword_highlight(self.local_tags[scope])

            if len(self.global_tags) == 0:
                out.write("\thi def link %s %s\n" % (self.name, self.highlight_group))

        if first_conditional_printed:
            out.write("endif\n")

        if len(self.global_tags) != 0:
            out.write("hi def link %s %s\n" % (self.name, self.highlight_group))

# Extracts information from an already existing keyword file. Right now we just
# support extracting keywords for generating a list of reserved keywords.
class SyntaxFile():
    keyword_rule_matcher = re.compile(r"^\s*syn(t(a(x)?)?)?\s+keyword\s+(?P<rule_name>\w+)\b(?P<rule_def>.*)")
    keyword_matcher = re.compile(r"\w+")
    keyword_arguments = set(["conceal", "cchar", "contained", "containedin",
                             "nextgroup", "transparent", "skipwhite",
                             "skipnl", "skipempty", "conceallevel",
                             "concealcursor"])
    SEARCH_DIRS = [
            "/usr/share/vim/vim*/syntax/",
    ]

    def _find_syntax_file(name):
        found = None

        for search_dir in SyntaxFile.SEARCH_DIRS:
            for path in iglob(search_dir):
                if name in os.listdir(path):
                    found = path + name
                    break

        if found == None:
            raise Exception("Syntax file %s not found in standard vim directories" % name)

        return found

    def is_keyword(word):
        if SyntaxFile.keyword_matcher.match(word) != None and \
           word not in SyntaxFile.keyword_arguments:
            return True
        else:
            return False

    def __init__(self, name):
        self.keywords = dict()

        for line in open(SyntaxFile._find_syntax_file(name)).readlines():
            rule = self.keyword_rule_matcher.match(line)

            if rule == None:
                continue

            rule_name = rule.group("rule_name")
            keywords = rule.group("rule_def").strip().split(" ")

            new_keywords = set([k for k in keywords if SyntaxFile.is_keyword(k)])
            if rule_name not in self.keywords:
                self.keywords[rule_name] = new_keywords
            else:
                self.keywords[rule_name] |= new_keywords
