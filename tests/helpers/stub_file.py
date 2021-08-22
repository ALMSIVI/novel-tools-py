class StubFile:
    def __init__(self, data=None, mode='rt', encoding='utf-8'):
        self.read_data = data
        self.mode = mode
        self.encoding = encoding

        self.write_data = ''
        self.writes = []

    def read(self):
        pass

    def readlines(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

    # TODO: iterator
