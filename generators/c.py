#!/usr/bin/python3
from sys import argv
from ctag import CTag
from syntax import KeywordHighlight
from copy import copy

keyword_highlights = list()

def add_tags(name, highlight_group, tag_list, tag_type):
	keyword_highlight = KeywordHighlight(name, highlight_group)

	for tag in tag_list:
		if tag.tag_type != tag_type:
			continue

		if tag.file_name.endswith(".h"):
			keyword_highlight.add_tag(tag)
		else:
			keyword_highlight.add_tag(tag, tag.file_name)

	keyword_highlights.append(keyword_highlight)

def generate_syntax(tag_list):
	tag_list = [tag for tag in tag_list if tag.language == "C++" or \
	                                       tag.language == "C"]

	add_tags("cFunctionTag", "Function", tag_list, "f")
	add_tags("cMacroTag",    "Macro",    tag_list, "d")
	add_tags("cEnumTag",     "Constant", tag_list, "e")
	add_tags("cTypeTag",     "Type",     tag_list, "t")
	add_tags("cStructTag",   "Type",     tag_list, "s")

	return keyword_highlights
