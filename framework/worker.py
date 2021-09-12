from .reader import Reader
from .processor import Processor
from .writer import Writer


class Worker:
    def __init__(self, readers: list[Reader], processors: list[Processor], writers: list[Writer]):
        self.readers = readers
        self.processors = processors
        self.writers = writers

    def work(self):
        for reader in self.readers:
            for obj in reader.read():
                for processor in self.processors:
                    obj = processor.process(obj)

                for writer in self.writers:
                    writer.write(obj)

        for writer in self.writers:
            writer.cleanup()
