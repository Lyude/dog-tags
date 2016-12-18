from multiprocessing import Pool
from fnmatch import fnmatch
from os import path
from sys import stderr, exit
from time import sleep
from functools import partial
from dogtags.ctag import CTag
from dogtags.syntax import KeywordHighlight

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

