import re
import json
from abc import ABC, abstractmethod

num_dict = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "廿": 20, "卅": 30, "卌": 40, "百": 100, "千": 1000}


def to_num(num: str) -> int:
    '''
    Converts a chinese string to a number.
    '''
    num = num.strip()
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


class MatchResult:
    '''
    - status (bool): whether the match is successful or not. If it is False, then the rest elements are garbage values.
    - title (str): the processed title name, if the match is successful.
    - index (int): a unique identifier for the title.
        - For regular titles, the ids should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the ids should be negative.
    '''

    def __init__(self, status: bool, index: int, title: str):
        self.status = status
        self.index = index
        self.title = title


class Matcher(ABC):
    @abstractmethod
    def match(self, line: str) -> MatchResult:
        '''Takes a line of string and attempts a match.'''
        pass

    @abstractmethod
    def format(self, result: MatchResult) -> str:
        '''Takes a match result and returns a formatted name.'''
        pass

    @abstractmethod
    def filename(self, result: MatchResult) -> str:
        '''Takes a match result and returns a valid filename.'''
        pass


class NumberedMatcher(Matcher):
    '''Matches a regular chapter/volume, with an index and/or a title.'''

    def __init__(self, args):
        '''
        Arguments:
        - regex: The regex to match for. It will contain two groups: the first group is the index, the second (optional) is the title.
        - format: The format for the chapter/volume.
        '''
        self.regex = re.compile(args['regex'])
        self.format_str = args['format']

    def match(self, line: str) -> MatchResult:
        m = self.regex.match(line)
        if m:
            try:
                index = to_num(m[1])
                title = m[2].strip()
                return MatchResult(True, index, title)
            except:  # Not a valid number
                return MatchResult(False, None, None)

        return MatchResult(False, None, None)

    def format(self, result: MatchResult) -> str:
        return self.format_str.format(index=result.index, title=result.title)

    def filename(self, result: MatchResult) -> str:
        return purify_name(self.format(result))


class SpecialMatcher(Matcher):
    '''Matches a special chapter, whose prefix is in the given dict.'''

    def __init__(self, args):
        '''
        Arguments:
        - prefixes: list of special names to match for.
        '''
        self.prefixes = args['prefixes']
        self.regex = re.compile(args['regex'].format(
            prefixes=f'({"|".join(self.prefixes)})'))
        self.format_str = args['format']

    def match(self, line: str) -> MatchResult:
        m = self.regex.match(line)
        if m:
            for i in range(len(self.prefixes)):
                if m[0] == self.prefixes[i]:
                    title = m[2].strip()
                    # Use negative number to avoid colliding with numbered titles
                    return MatchResult(True, -i - 1, title)

        return MatchResult(False, None, None)

    def format(self, result: MatchResult) -> str:
        return self.format_str.format(prefix=self.prefixes[-result.index - 1], title=result.title)

    def filename(self, result: MatchResult) -> str:
        return purify_name(self.format(result))


class VolumeMatcher(Matcher):
    '''
    Matches volumes by the given volume list.
    A volume object consists of 3 fields:
    - name: directory name to be generated,
    - volume: raw volume name (to be matched against),
    - volume_formatted (optional): formatted volume name. If it is not present, the raw volume name will be used.
    '''

    def __init__(self, args):
        '''
        Arguments:
        - volumes: list of volume-name correspondences.
        '''
        self.volumes = args['volumes']
        # We assume that the list of volumes is in order, and can only be matched from the beginning.
        # Therefore, we will keep track of the number of volumes that have already been matched.
        # If it exceeds the length of the list we stop matching.
        self.index = 0

    def match(self, line: str) -> MatchResult:
        if self.index >= len(self.volumes):
            return MatchResult(False, None, None)

        volume = self.volumes[self.index]
        if line == volume['volume']:
            self.index += 1
            title = volume.get('volume_formatted', volume['volume'])
            return MatchResult(True, self.index, title)

        return MatchResult(False, None, None)

    def format(self, result: MatchResult) -> str:
        # It is the user's job to ensure that 'volume' or 'volume_formatted' is the already formatted.
        return result.title

    def filename(self, result: MatchResult) -> str:
        return self.volumes[result.index]['name']


def getMatcher(name, args):
    '''
    Factory method to get a matcher based on its name.
    '''
    return globals()[name](args)
