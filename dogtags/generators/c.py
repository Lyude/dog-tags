#!/usr/bin/python3
from sys import argv
from dogtags.ctag import CTag
from dogtags.syntax import KeywordHighlight, SyntaxFile
from ..generator import GeneratorBase
from copy import copy

builtin_syntax_file = SyntaxFile("c.vim")

class Generator(GeneratorBase):
    extensions = ('.c', '.h')
    languages = {'C', 'C++'}
    filetypes = ('c', 'cpp')

    reserved_keywords = \
        builtin_syntax_file.keywords["cStatement"]    | \
        builtin_syntax_file.keywords["cLabel"]        | \
        builtin_syntax_file.keywords["cConditional"]  | \
        builtin_syntax_file.keywords["cRepeat"]       | \
        builtin_syntax_file.keywords["cType"]         | \
        builtin_syntax_file.keywords["cOperator"]     | \
        builtin_syntax_file.keywords["cStructure"]    | \
        builtin_syntax_file.keywords["cStorageClass"] | \
        builtin_syntax_file.keywords["cConstant"]

    tag_type_mapping = {
        "f": "cFunctionTag",
        "p": "cFunctionTag",
        "d": "cMacroTag",
        "e": "cEnumMemberTag",
        "t": "cTypeTag",
        "s": "cTypeTag",
        "g": "cTypeTag",
    }

    def __init__(self):
        super().__init__()

        for o in [
            KeywordHighlight("cFunctionTag", "Function"),
            KeywordHighlight("cMacroTag", "Macro"),
            KeywordHighlight("cEnumMemberTag", "Constant"),
            KeywordHighlight("cTypeTag", "Type")
        ]:
            self.register_highlight_object(o)

    @classmethod
    def process_tag(cls, tag, is_primary_tag_file):
        if super().process_tag(tag, is_primary_tag_file) == None:
            return
        if tag.tag_type not in cls.tag_type_mapping:
            return
        if tag.tag_name in cls.reserved_keywords:
            return
        if tag.tag_name.startswith("operator "):
            return

        from_header = tag.file_name.endswith(".h")
        if not (is_primary_tag_file or from_header):
            return

        return (tag, from_header)

    @classmethod
    def is_global(cls, tag):
        return tag.file_name.endswith(".h")

    def process_result(self, result):
        tag, from_header = result

        self.highlight_objects[self.tag_type_mapping[tag.tag_type]].add_tag(
            tag, scope=tag.file_name if not from_header else None)

del builtin_syntax_file
