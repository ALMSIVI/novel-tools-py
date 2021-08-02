from split.matchers import *

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