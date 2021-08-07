from .reader import Reader
from .processor import Processor
from .writer import Writer

class Worker:
    def __init__(self, reader: Reader, processors: list[Processor], writer: Writer):
        self.reader = reader
        self.processors = processors
        self.writer = writer

    def work(self):
        self.reader.before()
        for processor in self.processors:
            processor.before()
        self.writer.before()

        while obj := self.reader.read():
            for processor in self.processors:
                obj = processor.process(obj)

            self.writer.write(obj)

        self.reader.after()
        for processor in self.processors:
            processor.after()
        self.writer.after()
