#!/usr/bin/python3
from sys import argv
from ctag import CTag
from syntax import KeywordHighlight
from copy import copy

keyword_highlights = list()

def add_tags(name, highlight_group, c_tags, tag_type):
	keyword_highlight = KeywordHighlight(name, highlight_group)
	tags = CTag.filter_by_attr(c_tags, "tag_type", tag_type)

	for tag in tags:
		if tag.file_name.endswith(".h"):
			keyword_highlight.add_tag(tag)
		else:
			keyword_highlight.add_tag(tag, tag.file_name)

	keyword_highlights.append(keyword_highlight)

def generate_syntax(tags_list):
	c_tags = CTag.filter_by_attr(tags_list, "language", "C++") + \
		 CTag.filter_by_attr(tags_list, "language", "C")

	add_tags("cFunctionTag", "Function", c_tags, "f")
	add_tags("cMacroTag", "Macro", c_tags, "d")
	add_tags("cEnumTag", "Constant", c_tags, "e")
	add_tags("cTypeTag", "Type", c_tags, "t")
	add_tags("cStructTag", "Type", c_tags, "s")

	return keyword_highlights

if __name__ == "__main__":
	for keyword_highlight in generate_syntax(argv[1]):
		print(keyword_highlight)
