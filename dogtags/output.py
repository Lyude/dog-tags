class Output():
    def __init__(self):
        self.__in_new_line = False
        self.__at_start_of_line = True
        self.indent_level = 0

    def __call__(self, string, endline=True):
        if self.__in_new_line:
            self._out_func('\n')

        if self.__at_start_of_line:
            self._out_func("  " * self.indent_level)

        self._out_func(string)

        self.__in_new_line = endline
        self.__at_start_of_line = endline

class FileOutput(Output):
    def __init__(self, file):
        super().__init__()
        self._file = file

        try:
            file.seek(0)
        except Exception:
            pass

    def _out_func(self, string):
        self._file.write(string)

class StringOutput(Output):
    def __init__(self):
        super().__init__()
        self.str = ""

    def _out_func(self, string):
        self.str += string
