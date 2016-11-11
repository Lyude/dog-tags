#!/usr/bin/python3
import sys
import importlib
import argparse
from fnmatch import fnmatch
from os import path
from sys import stderr
from ctag import CTag
from syntax import KeywordHighlight

class ProgressIndicator():
	def __init__(self, tag_count):
		self.processed_count = 0
		self.filtered_count = 0
		self.tag_count = tag_count
		self.progress_str = "0/%d tags (0%%)" % tag_count

		stderr.write("Processed %s" % self.progress_str)
		stderr.flush()

	def update(self):
		stderr.write('\b' * len(self.progress_str))
		count = self.processed_count + self.filtered_count

		self.progress_str = "%d/%d tags (%d%%)" % ( \
				count, self.tag_count, (count / self.tag_count) * 100)
		stderr.write(self.progress_str)
		stderr.flush()

	def finish(self):
		stderr.write('\n')
		stderr.write("%d included, %d excluded (filtered %d%%)\n" % ( \
				self.processed_count, self.filtered_count,
				(self.filtered_count / self.tag_count) * 100))
		stderr.flush()

def parse_tag_file(args):
	tag_list = list()
	tag_lines = open(args.tag_file).readlines()

	progress = ProgressIndicator(len(tag_lines))

	for line in tag_lines:
		try:
			tag = CTag(line)

			if args.include != None and \
					not any(fnmatch(tag.file_name, glob) for glob in args.include):
			   progress.filtered_count += 1
			elif args.exclude != None and \
					any(fnmatch(tag.file_name, glob) for glob in args.exclude):
			   progress.filtered_count += 1
			else:
			   progress.processed_count += 1
			   tag_list.append(tag)

			progress.update()

		except CTag.NotTagException:
			pass

	progress.finish()

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

	stderr.write("Reading tag list...\n")
	tag_list = parse_tag_file(args)

	# TODO: Eventually I'll have some proper search logic to find generators
	# in paths that they would be installed to along with this script. Since
	# I don't have any way to install this script right now, we just search
	# based off of the location of this script
	sys.path.append(path.join(path.dirname(path.realpath(__file__)), "generators"))

	generator = importlib.import_module(args.filetype)
	stderr.write("Generating syntax highlighting...\n")
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
