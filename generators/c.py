#!/usr/bin/python3

from sys import argv
from ctag import CTag
from syntax import KeywordHighlight

keyword_highlights = list()

def add_function_tags(c_tags):
	global_tags = dict()
	local_tags = dict()
	keyword_highlight = KeywordHighlight("cFunctionTag", "Function")

	tags = CTag.filter_by_attr(c_tags, "tag_type", "f") + \
	       CTag.filter_by_attr(c_tags, "tag_type", "p")

	for tag in tags:
		if tag.tag_type == "p" and tag.file_name.endswith(".h"):
			global_tags[tag.tag_name] = tag

			if tag.tag_name in local_tags:
				local_tags.remove(local_tag.tag_name)
		else:
			if tag.tag_name in local_tags:
				continue

			local_tags[tag.tag_name] = tag

	keyword_highlight.add_tags(global_tags)
	for local_tag in local_tags:
		keyword_highlight.add_tags(tag, tag.file_name)

	keyword_highlights.append(keyword_highlight)

def add_tags(name, highlight_group, c_tags, tag_type):
	keyword_highlight = KeywordHighlight(name, highlight_group)
	tags = CTag.filter_by_attr(c_tags, "tag_type", tag_type)

	for tag in tags:
		if tag.file_name.endswith(".h"):
			keyword_highlight.add_tags(tag)
		else:
			keyword_highlight.add_tags(tag, tag.file_name)

	keyword_highlights.append(keyword_highlight)

def generate_syntax(tags_list):
	c_tags = CTag.filter_by_attr(tags_list, "language", "C++") + \
		 CTag.filter_by_attr(tags_list, "language", "C")

	add_function_tags(c_tags)
	add_tags("cMacroTag", "Macro", c_tags, "d")
	add_tags("cEnumTag", "Constant", c_tags, "e")
	add_tags("cTypeTag", "Type", c_tags, "t")

	return keyword_highlights

if __name__ == "__main__":
	for keyword_highlight in generate_syntax(argv[1]):
		print(keyword_highlight)
