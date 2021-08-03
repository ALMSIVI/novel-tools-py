class ValidateResult:
    '''
    - status (str): If there is no error in validation, this will be None. If there is an error (duplicate/missing), this will be the error message.
    - title (str): the processed title name, if the match is successful.
    - index (int): a unique identifier for the title.
        - For regular titles, the ids should be positive and self-increasing. This is required for duplicate/missing index detection.
        - For special titles, the ids should be negative.
    '''

    def __init__(self, error: str, index: int, title: str):
        self.error = error
        self.index = index
        self.title = title
