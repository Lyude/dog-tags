# What is this?

This is a set of scripts I've written for generating additional syntax highlighting files for vim that can be used to highlight defined functions, macros, etc. It's main purpose is to replace the original plugin I used for this, EasyTags, with something that generates far simpler (and as a result, faster) commands.

# How to use
Simply run `./generator.py <filetype> <tags_file>`, where `tags_file` is a CTags file. It will output the commands to perform the highlighting in vim to stdout.

# TODO:
- Come up with some sort of method for this to be installed system-wide
- Add some functions to KeywordHighlight so that the scope of keywords can be limited to the files that they're visible in
