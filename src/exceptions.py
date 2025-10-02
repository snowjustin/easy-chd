# UI exceptions
class ProgressBarException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

# Tooling exceptions
class ChdmanNotInstalledError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class FileFormatNotSupportedError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class SameFileExtensionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class OutputFileAlreadyExists(Exception):
    def __init__(self, *args):
        super().__init__(*args)