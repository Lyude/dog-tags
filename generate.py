#!/usr/bin/python3
import sys
import importlib
import argparse
from fnmatch import fnmatch
from os import path
from ctag import CTag
from syntax import KeywordHighlight

def parse_tag_file(args):
	tag_list = list()

	for line in open(args.tag_file).readlines():
		try:
			tag = CTag(line)

			if args.include != None and \
			   not any(fnmatch(tag.file_name, glob) for glob in args.include):
				continue

			if args.exclude != None and \
			   any(fnmatch(tag.file_name, glob) for glob in args.exclude):
				continue

			tag_list.append(tag)
		except CTag.NotTagException:
			pass

	return tag_list

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate vim syntax files using ctags")
	parser.add_argument('filetype', help="The filetype we're generating highlighting from")
	parser.add_argument('tag_file', help="The ctags file to use for generation")
	parser.add_argument('--exclude', '-e', help="Exclude tags from files matching this pattern",
					    metavar='pattern', action='append', dest='exclude')
	parser.add_argument('--include', '-i', help="Include only tags from files matching this pattern",
					    metavar='pattern', action='append', dest='include')
	args = parser.parse_args()

	tag_list = parse_tag_file(args)

	# TODO: Eventually I'll have some proper search logic to find generators
	# in paths that they would be installed to along with this script. Since
	# I don't have any way to install this script right now, we just search
	# based off of the location of this script
	sys.path.append(path.join(path.dirname(path.realpath(__file__)), "generators"))

	generator = importlib.import_module(args.filetype)
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
