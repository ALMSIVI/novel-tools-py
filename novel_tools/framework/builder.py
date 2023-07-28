from .data import Index, Source, Content, NovelData

# One common operation for this tool is merging NovelData objects. Often, we want new data to overwrite new data, if the
# fields of the new data is not None. The Builder pattern is employed here to hide these None checks.

class IndexBuilder:
    index: int
    sub_index: str | int
    tag: str
    order: int

    def set_index(self, index: int):
        if index is not None:
            self.index = index

    def set_sub_index(self, sub_index: str | int):
        if sub_index is not None:
