#!/usr/bin/python3

from sys import argv
from ctag import CTag
from syntax import KeywordHighlight

def generate_syntax(tags_list):
	c_tags = CTag.filter_by_attr(tags_list, "language", "C++") + \
		 CTag.filter_by_attr(tags_list, "language", "C")
	keyword_highlights = list()

	current_rule = KeywordHighlight("cFunctionTag", "Function")
	current_rule.add_tags(CTag.filter_by_attr(c_tags, "tag_type", "f"))
	keyword_highlights.append(current_rule)

	current_rule = KeywordHighlight("cMacroTag", "Macro")
	current_rule.add_tags(CTag.filter_by_attr(c_tags, "tag_type", "d"))
	keyword_highlights.append(current_rule)

	current_rule = KeywordHighlight("cEnumTag", "Constant")
	current_rule.add_tags(CTag.filter_by_attr(c_tags, "tag_type", "e"))
	keyword_highlights.append(current_rule)

	current_rule = KeywordHighlight("cTypeTag", "Type")
	current_rule.add_tags(CTag.filter_by_attr(c_tags, "tag_type", "t"))
	keyword_highlights.append(current_rule)

	return keyword_highlights

if __name__ == "__main__":
	for keyword_highlight in generate_syntax(argv[1]):
		print(keyword_highlight)
