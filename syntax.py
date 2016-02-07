#!/usr/bin/python3

class KeywordHighlight():
	def __init__(self, name, highlight_group):
		self.global_tags = set()
		self.local_tags = dict()

		self.name = name
		self.highlight_group = highlight_group

	def add_tag(self, tag, scope=None):
		if scope != None:
			if scope not in self.local_tags:
				self.local_tags[scope] = set()

			dest = self.local_tags[scope]
		else:
			dest = self.global_tags

		dest.add(tag.tag_name)

	def __str__(self):
		ret = ""

		if len(self.global_tags) != 0:
			ret += "syn keyword %s " % self.name

			for tag in self.global_tags:
				ret += tag + " "

			ret += "\n"

		for scope in self.local_tags.keys():
			ret += "if expand('%%:t') == '%s'\n" % scope
			ret += "\tsyn keyword %s " % self.name

			for tag in self.local_tags[scope]:
				ret += tag + " "

			ret += "\n"

			if len(self.global_tags) == 0:
				ret += "\thi def link %s %s\n" % (self.name, self.highlight_group)

			ret += "endif\n"

		if len(self.global_tags) != 0:
			ret += "hi def link %s %s\n" % (self.name, self.highlight_group)

		return ret
