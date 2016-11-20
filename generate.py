#!/usr/bin/python3
import sys
import importlib
import argparse
from multiprocessing import Pool
from fnmatch import fnmatch
from os import path
from sys import stderr, exit
from time import sleep
from functools import partial
from ctag import CTag
from syntax import KeywordHighlight

PROGRESS_INTERVAL = (1 / 60)
CHUNKSIZE = 5000

def parse_tag(include, exclude, work):
    try:
        tag = CTag(work)

        if (include and not any(fnmatch(tag.file_name, g) for g in include)) or \
           (exclude and any(fnmatch(tag.file_name, g) for g in exclude)):
            return None

        return tag
    except CTag.NotTagException:
        pass

def run_tag_parsers(args):
    pool = Pool()

    tag_lines = open(args.tag_file).readlines()
    tag_count = len(tag_lines)

    progress_str = "0/%d tags (0%%)" % tag_count
    stderr.write("Processed %s" % progress_str)
    stderr.flush()

    # Keeping an up to date progress meter while keeping this multiprocess is a
    # little difficult: if we give each worker the same Value(), they'll end up
    # all just contending the mutex for it, so each one needs their own Value
    # that
    result = pool.map_async(partial(parse_tag, args.include, args.exclude),
                            tag_lines, CHUNKSIZE)
    del tag_lines

    finished = False
    while not finished:
        finished = result.ready()
        processed = max(tag_count - (result._number_left * CHUNKSIZE), 0)

        stderr.write("\b" * len(progress_str))
        progress_str = "%d/%d tags (%d%%)" % (processed, tag_count,
                                              (processed / tag_count) * 100)
        stderr.write(progress_str)
        if finished:
            stderr.write("\n")
        stderr.flush()

        if not finished:
            result.wait(timeout=PROGRESS_INTERVAL)

    if not result.successful:
        stderr.write("Failed?\n")
        exit(1)

    return [r for r in result.get() if r != None]

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
    tag_list = run_tag_parsers(args)

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
