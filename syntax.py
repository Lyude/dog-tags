#!/usr/bin/python3

class KeywordHighlight():
	def __init__(self, name, highlight_group, preceding_keyword=None):
		self.global_tags = set()
		self.local_tags = dict()

		self.name = name
		self.highlight_group = highlight_group
		self.preceding_keyword = preceding_keyword

	def add_tag(self, tag, scope=None):
		if scope != None:
			if scope not in self.local_tags:
				self.local_tags[scope] = set()

			dest = self.local_tags[scope]
		else:
			dest = self.global_tags

		dest.add(tag.tag_name)

	def generate_script(self):
		def print_keyword_highlight(keywords):
			print("syn keyword %s %s" % \
			      (self.name, " ".join(keywords)), end="")

			if self.preceding_keyword != None:
				print(" containedin=%sPreceding" % self.name)
			else:
				print("")

		if self.preceding_keyword != None:
			print("syn match %sPreceding \"\(%s\s\)\@<=\S\+\" contains=%s transparent" % \
			      (self.name, self.preceding_keyword, self.name))

		if len(self.global_tags) != 0:
			print_keyword_highlight(self.global_tags)

		first_conditional_printed = False
		for scope in self.local_tags.keys():
			if first_conditional_printed:
				print("else", end="")
			else:
				first_conditional_printed = True

			print("if expand('%%:p') == '%s'" % scope)
			print("\t", end="")
			print_keyword_highlight(self.local_tags[scope])

			if len(self.global_tags) == 0:
				print("\thi def link %s %s" % (self.name, self.highlight_group))

		if first_conditional_printed:
			print("endif")

		if len(self.global_tags) != 0:
			print("hi def link %s %s" % (self.name, self.highlight_group))
