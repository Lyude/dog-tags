#!/usr/bin/python3

class KeywordHighlight(list):
	def __init__(self, name, highlight_group):
		self.name = name
		self.highlight_group = highlight_group

	def __str__(self):
		ret = "syn keyword %s " % self.name

		for keyword in self:
			ret += keyword.tag_name + " "

		ret += "\n"
		ret += "hi def link %s %s\n" % (self.name, self.highlight_group)

		return ret
