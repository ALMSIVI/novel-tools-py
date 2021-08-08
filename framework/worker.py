from .reader import Reader
from .processor import Processor
from .writer import Writer


class Worker:
    def __init__(self, reader: Reader, processors: list[Processor], writers: list[Writer]):
        self.reader = reader
        self.processors = processors
        self.writers = writers

    def work(self):
        self.reader.before()
        for processor in self.processors:
            processor.before()
        for writer in self.writers:
            writer.before()

        while obj := self.reader.read():
            for processor in self.processors:
                obj = processor.process(obj)

            for writer in self.writers:
                writer.write(obj)

        self.reader.after()
        for processor in self.processors:
            processor.after()
        for writer in self.writers:
            writer.after()
