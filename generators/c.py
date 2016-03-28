#!/usr/bin/python3
from sys import argv
from ctag import CTag
from syntax import KeywordHighlight
from copy import copy

keyword_highlights = list()

def add_tags(tag_list, name, highlight_group, tag_type, preceding_keyword=None):
	keyword_highlight = KeywordHighlight(name, highlight_group, preceding_keyword)

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

	add_tags(tag_list, "cFunctionTag",   "Function", "f")
	add_tags(tag_list, "cMacroTag",      "Macro",    "d")
	add_tags(tag_list, "cEnumMemberTag", "Constant", "e")
	add_tags(tag_list, "cTypeTag",       "Type",     "t")
	add_tags(tag_list, "cStructTag",     "Type",     "s", "struct")
	add_tags(tag_list, "cEnumTag",       "Type",     "g", "enum")

	return keyword_highlights
