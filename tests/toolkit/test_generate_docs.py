from pytest_mock import MockerFixture
from common import ACC, FieldMetadata
from toolkit import docgen


class StubACC(ACC):
    """Docstring."""

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return [
            FieldMetadata('test1', 'str', description='Test 1'),
            FieldMetadata('test2', 'int', optional=True, description='Test 2'),
            FieldMetadata('test3', 'bool', default=True, description='Test 3')
        ]


docstring = '''
- test1 (str): Test 1
- test2 (int, optional): Test 2
- test3 (bool, optional, default=True): Test 3
'''[1:-1]


def test_generate_docs(mocker: MockerFixture):
    mocker.patch('toolkit.generate_docs.generate_classes', return_value={'Default': {'StubACC': StubACC}})
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m().write

    docgen(None)
    handle.assert_has_calls([
        mocker.call('## Default\n\n'),
        mocker.call('### StubACC\n\n'),
        mocker.call('**Description:**\n\n'),
        mocker.call('Docstring.'),
        mocker.call('\n'),
        mocker.call('\n**Arguments:**\n\n'),
        mocker.call(docstring),
        mocker.call('\n'),
        mocker.call('\n')
    ])
