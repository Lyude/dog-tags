#!/usr/bin/python3
from sys import argv

class CTag():
    __slots__ = [
        'tag_name',
        'file_name',
        'ex_cmd',
        'tag_type',
        'extra_fields'
    ]

    class NotTagException(Exception):
        def __init__(self):
            super().__init__(self, "Failed to parse tag")

    def __init__(self, line):
        line = line.strip()

        try:
            fields = line.split("\t", 2);

            self.tag_name = fields[0]
            self.file_name = fields[1]

            fields = fields[2].split(";\"\t")
            self.ex_cmd = fields[0]

            fields = fields[1].split("\t")
            self.tag_type = fields[0]

            if fields:
                self.extra_fields = dict()

                for field in fields[1:]:
                    field_name, field_value = field.split(":", 1)
                    self.extra_fields[field_name] = field_value
        except Exception as e:
            raise CTag.NotTagException() from e

    def __getattr__(self, attr):
        try:
            return self.__getattribute__('extra_fields')[attr]
        except (KeyError, AttributeError):
            raise AttributeError("'CTag' object has no attribute '%s'" % attr)

    def __str__(self):
        self_str = "Tag name: %s\n" \
               "File name: %s\n" \
               "Ex command: %s\n" \
               "Type: %s\n" \
               % (self.tag_name, self.file_name, self.ex_cmd, self.tag_type)

        if self.extra_fields:
            for field_name in self.extra_fields:
                self_str += "%s: %s\n" % (field_name,
                                          self.extra_fields[field_name])

        return self_str;

    def __cmp__(self, other):
        try:
            for field in CTag.__slots__ + self.extra_fields.keys():
                if getattr(self, field) != getattr(other, field):
                    return False
        except AttributeError: # The other instance doesn't have all our fields
            return False

        return True

if __name__ == "__main__":
    tags_list = list()

    for line in open(argv[1]).readlines():
        try:
            tags_list.append(CTag(line))

        except CTag.NotTagException:
            pass

    for tag in tags_list:
        print(tag)
