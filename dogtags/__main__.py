#!/usr/bin/python3
import importlib
import argparse
from dogtags.generate import run_tag_parsers, FileOutput
from dogtags.generator import GeneratorBase
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

generator_module = importlib.import_module("dogtags.generators." +
                                           args.filetype)
assert hasattr(generator_module, "Generator")
assert issubclass(generator_module.Generator, GeneratorBase)

stderr.write("Reading tags...\n")
results = run_tag_parsers(args.tag_file, args.include, args.exclude,
                          generator_module.Generator)

stderr.write("Processing tags...\n")
generator = generator_module.Generator()
generator.process_results(results)

with ConditionalBlock(args.output,
                      " || ".join(['&ft == "%s"' % t for t in generator.filetypes])):
    generator.generate_init_code(args.output)
    for obj in generator.highlight_objects.values():
        obj.generate_script(args.output)

exit(0)
