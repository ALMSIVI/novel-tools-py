import re
import json
from abc import ABC, abstractmethod
from typing import Tuple

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
    return filename.translate(valid_filenames).strip()


class Matcher(ABC):
    @abstractmethod
    def match(self, line: str) -> Tuple[bool, str, int]:
        '''
        Takes a line of string and attempts a match.

        Returns a tuple that indicates the match result.

        - status (bool): whether the match is successful or not. If it is False, then the rest elements are garbage values.

        - title (str): the processed title name, if the match is successful.

        - id (str): a unique identifier for the title.

            - For regular titles, the ids should be positive and self-increasing for duplicate/missing title detection.

            - For special titles, they should be negative.
        '''
        pass


class NumberedMatcher(Matcher):
    def __init__(self, args):
        '''
        Arguments:

        - regex: The regex to match for.

        - start_index: the beginning of the number portion.

        - end_char: indicates the end of the number portion.
        '''
        self.regex = re.compile(args['regex'])
        self.start_index = args['start_index']
        self.end_char = args['end_char']

    def match(self, line: str) -> Tuple[bool, str, int]:
        if self.regex.match(line):
            end = line.index(self.end_char)
            try:
                number = to_num(line[self.start_index: end])
                return (True, purify_name(line[:self.start_index] + str(number) + line[end:-1]), number)
            except:  # Not a valid number
                return (False, None, None)

        return (False, None, None)


class SpecialMatcher(Matcher):
    def __init__(self, args):
        '''
        Arguments:

        - names: list of special names to match for.
        '''
        self.names = args['names']

    def match(self, line: str) -> Tuple[bool, str, int]:
        for i in range(len(self.names)):
            name = self.names[i]
            if line.startswith(name):
                # Use negative number to avoid colliding with numbered titles
                return (True, purify_name(line), -i - 1)

        return (False, None, None)


class VolumeMatcher(Matcher):
    def __init__(self, args):
        '''
        Arguments:

        - volumes: list of volume-name correspondences.
        '''
        self.volumes = args['volumes']
        self.index = 0

    def match(self, line: str) -> Tuple[bool, str, int]:
        if self.index >= len(self.volumes):
            return (False, None, None)
            
        volume = self.volumes[self.index]
        if line.startswith(volume['volume']):
            self.index += 1
            return (True, volume['name'], self.index)

        return (False, None, None)


def getMatcher(name, args):
    '''
    Factory method to get a matcher based on its name.
    '''
    return globals()[name](args)
