#!/usr/bin/python3
import re
import os
import datetime
from glob import iglob
from .version import __version__

class ConditionalBlock():
    """
    Generates simple conditional blocks to wrap around generated vimscript
    """
    def __init__(self, out, start_condition=None):
        self._out = out
        self._first_conditional = True
        if start_condition != None:
            self._start_condition = start_condition

    class UsageError(Exception):
        pass

    def __enter__(self):
        if hasattr(self, '_start_condition'):
            self.start_block(self._start_condition)
            del self._start_condition

        return self

    def __exit__(self, *exc):
        self.end_block()
        return False

    def start_block(self, condition=None):
        if self._first_conditional:
            if condition == None:
                raise ConditionalBlock.UsageError("First conditional cannot be empty")

            self._first_conditional = False
            self._out('if %s' % condition)
        else:
            self._out.indent_level -= 1

            self._out('else', endline=False)
            if condition != None:
                self._out('if %s' % condition, endline=False)
            self._out('')

        self._out.indent_level += 1

    def end_block(self):
        # Don't end a conditional we never started
        if self._first_conditional:
            return

        self._out.indent_level -= 1
        self._out('endif')

class TagScopeBlock(ConditionalBlock):
    """
    Generates simple conditional blocks that limit the scope of the contained
    vimscript to a certain file
    """
    def __init__(self, out):
        super().__init__(out=out)

    def start_block(self, scope=None):
        if scope != None:
            if scope.startswith('/'):
                lval = "expand('%:p')"
            else:
                lval = "s:rel_file"

            # Compare against the full path if the tag paths are absolute
            condition = "%s == '%s'" % (lval, scope)
        else:
            condition = None

        super().start_block(condition)

class KeywordHighlight():
    def __init__(self, name, highlight_group):
        self.global_tags = set()
        self.local_tags = dict()

        self.name = name
        self.highlight_group = highlight_group

    def add_tag(self, tag, scope=None):
        if scope != None:
            if scope not in self.local_tags:
                self.local_tags[scope] = set()

            dest = self.local_tags[scope]
        else:
            dest = self.global_tags

        dest.add(tag.tag_name)

    def generate_script(self, out):
        if len(self.global_tags) != 0:
            for tag in self.global_tags:
                out("syn keyword %s %s" % (self.name, tag))

        with TagScopeBlock(out) as block:
            for scope in self.local_tags.keys():
                block.start_block(scope)
                for tag in self.local_tags[scope]:
                    out("syn keyword %s %s" % (self.name, tag))

class SyntaxFile():
    """
    Extracts information from an already existing keyword file. Right now we
    just support extracting keywords for generating a list of reserved keywords.
    """
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

def generate_init_script(args):
    """
    Generates vimscript that sets up state required by other classes in this
    module. Must be called before using a GeneratorBase.
    """
    out = args.output

    out('" Generated by dog-tags v%s' % __version__)

    dirname = os.path.dirname(args.tag_file.name) + os.path.sep
    out("let s:rel_file = @%")
    with ConditionalBlock(out) as if_block:
        # Remove leading ./ on @%, if any
        if_block.start_block('stridx(s:rel_file, ".%s") == 0' % os.path.sep)
        out("let s:rel_file = strpart(s:rel_file, %d)" % len('.' + os.path.sep))

        # Make @% relative to the directory containing the tags file
        if_block.start_block('stridx(s:rel_file, "%s") == 0' % dirname)
        out("let s:rel_file = strpart(s:rel_file, %d)" % len(dirname))
