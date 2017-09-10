#!/usr/bin/python3
import importlib
import argparse
from dogtags.output import FileOutput
from dogtags.workers import run_tag_parsers
from dogtags.generator import GeneratorBase
from dogtags.syntax import ConditionalBlock, generate_init_script
from dogtags.version import __version__
from sys import stderr, stdout, exit

def parse_filetype(arg):
    try:
        return importlib.import_module('dogtags.generators.' + arg)
    except ModuleNotFoundError:
        raise argparse.ArgumentTypeError("'%s' generator not found" % arg)

def parse_output(arg):
    try:
        return FileOutput(open(arg, 'w'))
    except OSError as e:
        raise argparse.ArgumentTypeError(
            "Can't open '%s': %s" % (arg, e.strerror))

parser = argparse.ArgumentParser(description="Generate vim syntax files using ctags")
parser.add_argument('filetype',
                    help="The filetype we're generating highlighting from",
                    type=parse_filetype)
parser.add_argument('tag_file', help="The ctags file to use for generation",
                    type=argparse.FileType('r'))
parser.add_argument('-V', '--version', action='version', version=__version__)
parser.add_argument('-e', '--exclude', help="Exclude tags from files matching this pattern",
                    metavar='PATTERN', action='append')
parser.add_argument('-i', '--include', help="Include only tags from files matching this pattern",
                    metavar='PATTERN', action='append')
parser.add_argument('-o', '--output',
                    help="Where to output the generated syntax file (default is /dev/stdout)",
                    type=parse_output, default=FileOutput(stdout))
parser.add_argument('-a', '--add-library',
                    help="Include globally visible tags from another project in the output",
                    action='append', type=argparse.FileType(), dest='libraries')
args = parser.parse_args()

generator_module = args.filetype
assert hasattr(generator_module, "Generator")
assert issubclass(generator_module.Generator, GeneratorBase)

stderr.write("Reading tags...\n")
results = list()
if args.libraries:
    for tag_file in args.libraries:
        results.append(iter(run_tag_parsers(tag_file, False,
                                            args.include, args.exclude,
                                            generator_module.Generator)))

results.append(iter(run_tag_parsers(args.tag_file, True,
                                    args.include, args.exclude,
                                    generator_module.Generator)))

stderr.write("Processing tags...\n")
generator = generator_module.Generator()
for i in results:
    for result in i:
        generator.process_result(result)

try:
    generate_init_script(args)
    with ConditionalBlock(args.output,
                          " || ".join(['&ft == "%s"' % t for t in generator.filetypes])):
        generator.generate_init_code(args.output)
        for obj in generator.highlight_objects.values():
            obj.generate_script(args.output)

        generator.generate_fini_code(args.output)
except BrokenPipeError as e:
    # Broken pipe errors on stdout will happen whenever we're interrupted,
    # silence them
    if args.output._file is stdout:
        stderr.close()

    raise e from e

exit(0)
