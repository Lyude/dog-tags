#!/usr/bin/python3

class KeywordHighlight():
	def __init__(self, name, highlight_group):
		self.global_tags = list()

		self.name = name
		self.highlight_group = highlight_group

	def add_tags(self, tags):
		if hasattr(tags, "__iter__"):
			for tag in tags:
				self.add_tags(tag)

			return


		self.global_tags.append(tags)

	def __str__(self):
		ret = "syn keyword %s " % self.name

		for keyword in self.global_tags:
			ret += keyword.tag_name + " "

		ret += "\n"
		ret += "hi def link %s %s\n" % (self.name, self.highlight_group)

		return ret
