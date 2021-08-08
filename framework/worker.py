from .reader import Reader
from .processor import Processor
from .writer import Writer


class Worker:
    def __init__(self, reader: Reader, processors: list[Processor], writers: list[Writer]):
        self.reader = reader
        self.processors = processors
        self.writers = writers

    def work(self):
        while obj := self.reader.read():
            for processor in self.processors:
                obj = processor.process(obj)

            for writer in self.writers:
                writer.write(obj)

        self.reader.cleanup()
        for processor in self.processors:
            processor.cleanup()
        for writer in self.writers:
            writer.cleanup()
