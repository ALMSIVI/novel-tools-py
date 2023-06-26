from pydantic import BaseModel, Field
from pytest_mock import MockerFixture
from novel_tools.utils import Stage
from novel_tools.toolkit import docgen


class StubOptions(BaseModel):
    test1: str = Field(description='Test 1')
    test2: int | None = Field(description='Test 2')
    test3: bool = Field(default=True, description='Test 3')


class StubStage:
    """Docstring."""
    pass


docstring = '''
- test1 (str): Test 1
- test2 (int, optional): Test 2
- test3 (bool, optional, default=True): Test 3
'''[1:-1]


def test_generate_docs(mocker: MockerFixture):
    mocker.patch('novel_tools.toolkit.generate_docs.get_all_classes',
                 return_value={Stage.readers: {'StubStage': (StubStage, StubOptions)}})
    m = mocker.patch('pathlib.Path.open', mocker.mock_open())
    handle = m().write

    docgen(None)
    handle.assert_has_calls([
        mocker.call('## Readers\n\n'),
        mocker.call('### StubStage\n\n'),
        mocker.call('**Description:**\n\n'),
        mocker.call('Docstring.'),
        mocker.call('\n'),
        mocker.call('\n**Arguments:**\n\n'),
        mocker.call(docstring),
        mocker.call('\n'),
        mocker.call('\n')
    ])
