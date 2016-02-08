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

	def generate_script(self):
		if len(self.global_tags) != 0:
			print("syn keyword %s %s" % (self.name, " ".join(self.global_tags)))

		first_conditional_printed = False
		for scope in self.local_tags.keys():
			if first_conditional_printed:
				print("else", end="")
			else:
				first_conditional_printed = True

			print("if expand('%%:p') == '%s'" % scope)
			print("\tsyn keyword %s %s" % (self.name, " ".join(self.local_tags[scope])))

			if len(self.global_tags) == 0:
				print("\thi def link %s %s" % (self.name, self.highlight_group))

		if first_conditional_printed:
			print("endif")

		if len(self.global_tags) != 0:
			print("hi def link %s %s" % (self.name, self.highlight_group))
