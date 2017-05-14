import fnmatch
import re

from multiprocessing import Pool, Array, cpu_count, RLock, Value
from sys import stderr, exit
from ctypes import c_int
from functools import partial
from dogtags.ctag import CTag
from math import ceil

PROGRESS_INTERVAL = (1 / 30)

class Output():
    def __init__(self):
        self._in_new_line = False
        self._at_start_of_line = True
        self.indent_level = 0

    def __call__(self, string, endline=True):
        if self._in_new_line:
            self._out_func('\n')

        if self._at_start_of_line:
            self._out_func("  " * self.indent_level)

        self._out_func(string)

        self._in_new_line = endline
        self._at_start_of_line = endline

class FileOutput(Output):
    def __init__(self, file):
        super().__init__()
        self._file = file

        try:
            file.seek(0)
        except Exception:
            pass

    def _out_func(self, string):
        self._file.write(string)

class StringOutput(Output):
    def __init__(self):
        super().__init__()
        self.str = ""

    def _out_func(self, string):
        self.str += string

class TagProcessorContext():
    """
    Stores the context for each tag processing worker

    Arguments:
        counts -- The array shared by each tag processing worker, each element
                  contains the number of tags processed by the respective
                  worker.
        count_pos -- The position of this worker in counts
        include -- The list of files to include tags from
        exclude -- The list of files to not include tags from
    """
    def __init__(self, counts, count_pos, include, exclude):
        self.counts = counts
        self.count_pos = count_pos
        self.include = include
        self.exclude = exclude

def parse_tag(languages, extensions, work):
    global context

    try:
        tag = CTag(work)
    except CTag.NotTagException:
        return
    else:
        try:
            if tag.language not in languages:
                return
        except AttributeError:
            # Fall back to checking file extensions
            if not any(tag.file_name.endswith(e) for e in extensions):
                return

        if context.include and not \
           any(g.match(tag.file_name) for g in context.include):
            return
        if context.exclude and \
           any(g.match(tag.file_name) for g in context.exclude):
            return
    finally:
        context.counts[context.count_pos] += 1

    return tag

def parser_init(counts, pos, include, exclude):
    global context

    with pos.get_lock():
        count_pos = pos.value
        pos.value += 1

    context = TagProcessorContext(counts, count_pos, include, exclude)

def run_tag_parsers(tag_file, include, exclude, languages, extensions):
    counts = Array(c_int._type_, cpu_count(), lock=False)

    # Create pre-compiled regex matches for all of our include/exclude globs
    if include:
        include = [re.compile(fnmatch.translate(glob)) for glob in include]
    if exclude:
        exclude = [re.compile(fnmatch.translate(glob)) for glob in exclude]

    pool = Pool(initializer=parser_init,
                initargs=[counts, Value(c_int, 0, lock=RLock()),
                          include, exclude])

    tag_lines = tag_file.readlines()
    tag_count = len(tag_lines)

    progress_str = "0/%d tags (0%%)" % tag_count
    stderr.write("Processed %s" % progress_str)
    stderr.flush()

    result = pool.map_async(partial(parse_tag, languages, extensions),
                            tag_lines, chunksize=ceil(tag_count / cpu_count()))
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

