from novel_tools.framework import NovelData, Processor


class OrderTransformer(Processor):
    """
    Assigns an order to the data. This could be useful for file writers, since the filenames won't keep the original
    order of reading. For example, one can append this order before all volume and chapter filenames to maintain
    ordering.
    """

    # noinspection PyUnusedLocal
    def __init__(self, args):
        self.orders = {}

    def process(self, data: NovelData) -> NovelData:
        if data.type not in self.orders:
            self.orders[data.type] = 0

        self.orders[data.type] += 1
        data.set(order=self.orders[data.type])
        return data
