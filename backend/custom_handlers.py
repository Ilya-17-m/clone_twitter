import logging


class CustomFileHandler(logging.Handler):

    def __init__(self, file_name: str, mode='a'):
        super().__init__()
        self.file_name = file_name
        self.mode = mode

    def emit(self, record):
        message = self.format(record)
        with open(file=self.file_name, mode=self.mode) as file:
            file.write(message)
