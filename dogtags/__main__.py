#!/usr/bin/python3
import importlib
import argparse
from dogtags.generate import run_tag_parsers, FileOutput
from dogtags.syntax import ConditionalBlock
from dogtags.version import __version__
from sys import stderr, stdout, exit

parser = argparse.ArgumentParser(description="Generate vim syntax files using ctags")
parser.add_argument('filetype', help="The filetype we're generating highlighting from")
parser.add_argument('tag_file', help="The ctags file to use for generation",
                    type=argparse.FileType('r'))
parser.add_argument('-V', '--version', action='version', version=__version__)
parser.add_argument('-e', '--exclude', help="Exclude tags from files matching this pattern",
                    metavar='pattern', action='append', dest='exclude')
parser.add_argument('-i', '--include', help="Include only tags from files matching this pattern",
                    metavar='pattern', action='append', dest='include')
parser.add_argument('-o', '--output',
                    help="Where to output the generated syntax file (default is /dev/stdout)",
                    type=lambda output: FileOutput(open(output, 'w')),
                    default=FileOutput(stdout))
args = parser.parse_args()

generator = importlib.import_module("dogtags.generators." + args.filetype)

stderr.write("Reading tag list...\n")
tag_list = run_tag_parsers(args.tag_file, args.include, args.exclude,
                           generator.languages)

stderr.write("Generating syntax highlighting...\n")
syntax = generator.generate_syntax(tag_list)

# Make sure that the tags file doesn't add tags for any other languages then
# the one we're generating for
with ConditionalBlock(args.output,
                      " || ".join(['&ft == "%s"' % t for t in generator.filetypes])):
    # Clear the current syntax in vim in case the script's loaded multiple
    # times to update highlighting rules
    for name in set([h.name for h in syntax]):
        with ConditionalBlock(args.output, 'hlexists("%s")' % name):
            args.output("syn clear %s" % name)

    for highlight in syntax:
        highlight.generate_script(args.output)

exit(0)
