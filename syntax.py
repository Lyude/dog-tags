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
		def p(output):
			print(output, end="")

		if len(self.global_tags) != 0:
			p("syn keyword %s " % self.name)

			for tag in self.global_tags:
				p(tag + " ")

			p("\n")

		for scope in self.local_tags.keys():
			p("if expand('%%:t') == '%s'\n" % scope)
			p("\tsyn keyword %s " % self.name)

			for tag in self.local_tags[scope]:
				p(tag + " ")

			p("\n")

			if len(self.global_tags) == 0:
				p("\thi def link %s %s\n" % (self.name, self.highlight_group))

			p("endif\n")

		if len(self.global_tags) != 0:
			p("hi def link %s %s\n" % (self.name, self.highlight_group))
