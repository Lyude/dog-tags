#!/usr/bin/python3
import sys
import importlib
from ctag import CTag
from syntax import KeywordHighlight

def parse_tag_file(path):
	tag_list = list()

	for line in open(path).readlines():
		try:
			tag_list.append(CTag(line))
		except CTag.NotTagException:
			pass

	return tag_list

if __name__ == "__main__":
	if len(sys.argv) < 3:
		sys.stderr.write("Usage: generate.py <filetype> <tag_file>\n")
		exit(1)

	filetype = sys.argv[1]
	tag_file = sys.argv[2]
	tag_list = parse_tag_file(tag_file)

	sys.path.append("./generators")

	generator = importlib.import_module(filetype)
	syntax = generator.generate_syntax(tag_list)

	for highlight in syntax:
		print(highlight)
