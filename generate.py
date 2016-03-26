#!/usr/bin/python3
import sys
import importlib
from os import path
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

	# TODO: Eventually I'll have some proper search logic to find generators
	# in paths that they would be installed to along with this script. Since
	# I don't have any way to install this script right now, we just search
	# based off of the location of this script
	sys.path.append(path.join(path.dirname(path.realpath(__file__)), "generators"))

	generator = importlib.import_module(filetype)
	syntax = generator.generate_syntax(tag_list)

	# Clear the current syntax in vim in case the script's loaded multiple
	# times to update highlighting rules
	print("if exists(\"b:dog_tags_run\")")

	for highlight in syntax:
		print("\tsyn clear %s" % highlight.name)

	print("endif")
	print("")
	print("let b:dog_tags_run=1")
	print("")

	for highlight in syntax:
		highlight.generate_script()
