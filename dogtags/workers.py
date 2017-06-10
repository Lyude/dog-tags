import fnmatch
import re

from sys import stderr, exit
from math import ceil
from ctypes import c_int
from multiprocessing import Pool, Array, cpu_count, RLock, Value
from dogtags.ctag import CTag
from dogtags.generator import GeneratorBase

PROGRESS_INTERVAL = (1 / 30)

class TagProcessorContext():
    """
    Stores the context for each tag processing worker

    Arguments:
        counts -- The array shared by each tag processing worker, each element
                  contains the number of tags processed by the respective
                  worker
        count_pos -- The position of this worker in counts
        is_primary -- Whether or not this tag file is the primary tag file
        include -- The list of files to include tags from
        exclude -- The list of files to not include tags from
        generator -- GeneratorBase() compatible object with handlers to process
                     tags in each worker
    """
    def __init__(self, counts, count_pos, is_primary, include, exclude,
                 generator):
        self.counts = counts
        self.count_pos = count_pos
        self.is_primary = is_primary
        self.include = include
        self.exclude = exclude
        self.generator = generator

def parse_tag(work):
    global context

    try:
        tag = CTag(work)
    except CTag.NotTagException:
        return
    else:
        if context.is_primary:
            if context.include and not \
               any(g.match(tag.file_name) for g in context.include):
                return
            if context.exclude and \
               any(g.match(tag.file_name) for g in context.exclude):
                return

        return context.generator.process_tag(tag, context.is_primary)
    finally:
        context.counts[context.count_pos] += 1

def parser_init(counts, pos, is_primary, include, exclude, generator):
    global context

    with pos.get_lock():
        count_pos = pos.value
        pos.value += 1

    context = TagProcessorContext(counts, count_pos, is_primary,
                                  include, exclude, generator)

def run_tag_parsers(tag_file, is_primary, include, exclude, generator):
    counts = Array(c_int._type_, cpu_count(), lock=False)

    # Create pre-compiled regex matches for all of our include/exclude globs
    if include:
        include = [re.compile(fnmatch.translate(glob)) for glob in include]
    if exclude:
        exclude = [re.compile(fnmatch.translate(glob)) for glob in exclude]

    pool = Pool(initializer=parser_init,
                initargs=[counts, Value(c_int, 0, lock=RLock()),
                          is_primary, include, exclude, generator])

    tag_lines = tag_file.readlines()
    tag_count = len(tag_lines)

    progress_str = "0/%d tags (0%%)" % tag_count
    stderr.write("%s: Processed %s" % (tag_file.name, progress_str))
    stderr.flush()

    result = pool.map_async(parse_tag, tag_lines,
                            chunksize=ceil(tag_count / cpu_count()))
    del tag_lines
    pool.close()

    finished = False
    while not finished:
        finished = result.ready()
        processed = 0
        for count in counts:
            processed += count

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

