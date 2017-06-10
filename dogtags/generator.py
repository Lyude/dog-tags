#!/usr/bin/python3

from abc import ABC, abstractmethod
from dogtags.syntax import ConditionalBlock

class UsageError(Exception):
    """ Thrown when you, the programmer, have done something wrong """
    pass

class GeneratorBase(ABC):
    @classmethod
    def process_tag(cls, tag, is_primary):
        """
        Processes a single parsed tag, and decides whether or not we want it to 
        be passed on to the final tag analysis method, process_tag_list. Called
        from a tag processing worker when reading in the tags file.

        By default, this checks to make sure that the tag has a filename with an
        extension defined in cls.extensions or a language type (if included in
        the tag file) and if so, returns the tag unmodified.

        This function can be overriden to add extra tag analysis to be performed
        on each read tag. Results for additional analysis can be returned from
        here.

        Arguments:
             tag -- The tag to process
             is_primary -- Whether or not this tag is from the primary tag file

        Returns: True to filter out the tag, False otherwise
        """
        try:
            if tag.language not in cls.languages:
                return
        except AttributeError:
            # Fall back to checking file extensions
            if not any(tag.file_name.endswith(e) for e in cls.extensions):
                return

        return tag

    @abstractmethod
    def __init__(self):
        """ Highlight objects should be registered here """
        self.__highlight_objects = dict()

    @property
    def highlight_objects(self):
        """
        The currently registered highlight objects
        """
        return self.__highlight_objects

    def register_highlight_object(self, highlight_object):
        """
        Register a new highlight object in the context of the current generator,
        this highlight object will included in the outputted vimscript.
        """
        try:
            self.__highlight_objects[highlight_object.name] = highlight_object
        except AttributeError:
            raise UsageError("%s.__init__() not called" %
                             self.__class__.__name__)

    def generate_init_code(self, out):
        """
        Generates vimscript intended to clear the current highlighting state
        before adding the actual syntax highlighting.

        By default, this generates code to clear any registered highlight
        objects.
        """
        for group in self.highlight_objects.values():
            with ConditionalBlock(out, 'hlexists("%s")' % group.name):
                out("syn clear %s" % group.name)

    @property
    @abstractmethod
    def filetypes(self):
        """ The vim filetypes this generator supports """
        raise NotImplemented()

    @abstractmethod
    def process_result(self, tag, is_primary_tag_file):
        """
        Populates the registered highlight objects using the given tag, which
        will be output into vimscript form after this completes.
        """
        raise NotImplemented()
