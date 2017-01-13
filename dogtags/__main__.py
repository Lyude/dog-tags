#!/usr/bin/python3
import importlib
import argparse
from dogtags.generate import run_tag_parsers
from dogtags.syntax import ConditionalBlock
from sys import stderr, exit

parser = argparse.ArgumentParser(description="Generate vim syntax files using ctags")
parser.add_argument('filetype', help="The filetype we're generating highlighting from")
parser.add_argument('tag_file', help="The ctags file to use for generation",
                    type=argparse.FileType('r'))
parser.add_argument('-e', '--exclude', help="Exclude tags from files matching this pattern",
                    metavar='pattern', action='append', dest='exclude')
parser.add_argument('-i', '--include', help="Include only tags from files matching this pattern",
                    metavar='pattern', action='append', dest='include')
parser.add_argument('-o', '--output',
                    help="Where to output the generated syntax file (default is /dev/stdout)",
                    type=argparse.FileType('w+'), default='-')
args = parser.parse_args()

stderr.write("Reading tag list...\n")
tag_list = run_tag_parsers(args.tag_file, args.include, args.exclude)

generator = importlib.import_module("dogtags.generators." + args.filetype)
stderr.write("Generating syntax highlighting...\n")
syntax = generator.generate_syntax(tag_list)

# Clear the current syntax in vim in case the script's loaded multiple
# times to update highlighting rules
with ConditionalBlock(args.output, 'exists("b:dog_tags_run")'):
    for highlight in syntax:
        args.output.write("\tsyn clear %s\n" % highlight.name)

args.output.write("\nlet b:dog_tags_run=1\n\n")

for highlight in syntax:
    highlight.generate_script(args.output)

exit(0)
