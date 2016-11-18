#!/usr/bin/python3
from sys import argv
from ctag import CTag
from syntax import KeywordHighlight, SyntaxFile
from copy import copy

keyword_highlights = list()

def add_tags(tag_list, reserved_keywords, name, highlight_group, tag_type, preceding_keyword=None):
    keyword_highlight = KeywordHighlight(name, highlight_group, preceding_keyword)

    for tag in tag_list:
        if tag.tag_type != tag_type or tag.tag_name in reserved_keywords:
            continue

        if tag.file_name.endswith(".h"):
            keyword_highlight.add_tag(tag)
        else:
            keyword_highlight.add_tag(tag, tag.file_name)

    keyword_highlights.append(keyword_highlight)

def generate_reserved_keywords():
    builtin_file = SyntaxFile("/usr/share/vim/vim74/syntax/c.vim")

    reserved_keywords = \
            builtin_file.keywords["cStatement"] | \
            builtin_file.keywords["cLabel"] | \
            builtin_file.keywords["cConditional"] | \
            builtin_file.keywords["cRepeat"] | \
            builtin_file.keywords["cType"] | \
            builtin_file.keywords["cOperator"] | \
            builtin_file.keywords["cStructure"] | \
            builtin_file.keywords["cStorageClass"] | \
            builtin_file.keywords["cConstant"]

    return reserved_keywords

def generate_syntax(tag_list):
    tag_list = [tag for tag in tag_list if tag.language == "C++" or \
                                           tag.language == "C"]
    reserved_keywords = generate_reserved_keywords()

    add_tags(tag_list, reserved_keywords, "cFunctionTag",   "Function", "f")
    add_tags(tag_list, reserved_keywords, "cMacroTag",      "Macro",    "d")
    add_tags(tag_list, reserved_keywords, "cEnumMemberTag", "Constant", "e")
    add_tags(tag_list, reserved_keywords, "cTypeTag",       "Type",     "t")
    add_tags(tag_list, reserved_keywords, "cStructTag",     "Type",     "s", "struct")
    add_tags(tag_list, reserved_keywords, "cEnumTag",       "Type",     "g", "enum")

    return keyword_highlights
