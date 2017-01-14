from multiprocessing import Pool, Array, cpu_count, RLock, Value
from fnmatch import fnmatch
from os import path
from sys import stderr, exit
from time import sleep
from ctypes import c_int
from functools import partial
from dogtags.ctag import CTag

PROGRESS_INTERVAL = (1 / 30)

count_pos = 0
counts = Array(c_int._type_, cpu_count(), lock=False)

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

    def _out_func(self, string):
        self._file.write(string)

class StringOutput(Output):
    def __init__(self):
        super().__init__()
        self.str = ""

    def _out_func(self, string):
        self.str += string

def parse_tag(include, exclude, work):
    global count_pos
    global counts

    tag = None
    try:
        tag = CTag(work)

        if (include and not any(fnmatch(tag.file_name, g) for g in include)) or \
           (exclude and any(fnmatch(tag.file_name, g) for g in exclude)):
            tag = None
    except CTag.NotTagException:
        pass

    counts[count_pos] += 1
    return tag

def parser_init(pos):
    global count_pos
    global counts
    with pos.get_lock():
        count_pos = pos.value
        pos.value += 1

    counts = counts

def run_tag_parsers(tag_file, include, exclude):
    global counts
    pool = Pool(initializer=parser_init,
                initargs=[Value(c_int, 0, lock=RLock())])

    tag_lines = tag_file.readlines()
    tag_count = len(tag_lines)

    progress_str = "0/%d tags (0%%)" % tag_count
    stderr.write("Processed %s" % progress_str)
    stderr.flush()

    result = pool.map_async(partial(parse_tag, include, exclude),
                            tag_lines, chunksize=int(tag_count / cpu_count()))
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

