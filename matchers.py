import re
import json
from abc import ABC, abstractmethod

num_dict = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "廿": 20, "卅": 30, "卌": 40, "百": 100, "千": 1000}


def to_num(num: str) -> int:
    '''
    Converts a chinese string to a number.
    '''

    try:
        value = int(num)
    except:
        value = 0
        digit = 1

        for i in range(len(num)):
            v = num_dict[num[i]]
            if v >= 10:
                digit *= v
                value += digit
            elif i == len(num) - 1:
                value += v
            else:
                digit = v

    return value


valid_filenames = dict((ord(char), None) for char in '\/*?:"<>|\n')


def purify_name(filename: str) -> str:
    return filename.translate(valid_filenames)


class Matcher(ABC):
    @abstractmethod
    def match(self, line: str):
        pass


class NumberedMatcher(Matcher):
    def __init__(self, args):
        self.regex = re.compile(args['regex'])
        self.start_index = args['start_index']
        self.end_char = args['end_char']

    def match(self, line: str):
        if self.regex.match(line):
            end = line.index(self.end_char)
            try:
                number = str(to_num(line[self.start_index: end]))
                return (True, purify_name(line[:self.start_index] + number + line[end:-1]))
            except:
                return (False, None)

        return (False, None)


class SpecialMatcher(Matcher):
    def __init__(self, args):
        self.names = args['names']

    def match(self, line: str):
        for name in self.names:
            if line.startswith(name):
                return (True, purify_name(line))

        return (False, None)


class VolumeMatcher(Matcher):
    def __init__(self, args):
        self.volumes = args['volumes']

    def match(self, line: str):
        for volume in self.volumes:
            if line.startswith(volume['volume']):
                return (True, volume['name'])

        return (False, None)


def getMatcher(name, args):
    return globals()[name](args)
