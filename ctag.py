#!/usr/bin/python3
from sys import argv

class CTag():
	extra_field_names = None

	class NotTagException(Exception):
		def __init__(self):
			super().__init__(self, "Failed to parse tag")

	def __init__(self, line):
		fields = line.split("\t", 2);

		if len(fields) < 3:
			raise CTag.NotTagException()

		self.tag_name = fields[0]
		self.file_name = fields[1]

		fields = fields[2].split(";\"\t")
		if len(fields) < 2:
			raise CTag.NotTagException()

		self.ex_cmd = fields[0]

		fields = fields[1].split("\t")
		if len(fields) < 1:
			raise CTag.NotTagException()

		self.tag_type = fields[0]

		if len(fields) > 1:
			self.extra_field_names = list()

			for field in fields[1:]:
				pair = field.split(":", 1)
				setattr(self, pair[0], pair[1])
				self.extra_field_names.append(pair[0])

	def __str__(self):
		self_str = "Tag name: %s\n" \
			   "File name: %s\n" \
			   "Ex command: %s\n" \
			   "Type: %s\n" \
			   % (self.tag_name, self.file_name, self.ex_cmd, self.tag_type)

		if self.extra_field_names != None:
			for field_name in self.extra_field_names:
				self_str += "%s: %s\n" % (field_name, getattr(self, field_name))

		return self_str;

	def __cmp__(self, other):
		if self.tag_name != other.tag_name or \
		   self.file_name != other.file_name or \
		   self.ex_cmd != other.ex_cmd or \
		   self.tag_type != other.tag_type or \
		   self.extra_field_names != other.extra_field_names:
			   return False

		if self.extra_field_names != None:
			for field in self.extra_field_names:
				if getattr(self, field) != getattr(other, field):
					return False

		return True

	def filter_by_attr(list, attr, value):
		return [tag for tag in list if hasattr(tag, attr) and \
					       getattr(tag, attr) == value]

if __name__ == "__main__":
	tags_list = list()

	for line in open(argv[1]).readlines():
		try:
			tags_list.append(CTag(line))

		except CTag.NotTagException:
			pass

	for tag in tags_list:
		print(tag)

	print("---- Filtering List ----")
	for tag in CTag.filter_by_attr(tags_list, "language", "Sh"):
		print(tag)
