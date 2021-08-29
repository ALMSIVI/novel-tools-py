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
    p = mocker.patch('toolkit.generate_docs.generate_classes', return_value={'Default': {'StubACC': StubACC}})
    m = mocker.patch('builtins.open', mocker.mock_open())
    handle = m()

    docgen(None)
    handle.write.assert_any_call('## Default\n\n')
    handle.write.assert_any_call('### StubACC\n\n')
    handle.write.assert_any_call('**Description:**\n')
    handle.write.assert_any_call('Docstring.')
    handle.write.assert_any_call('\n**Arguments:**\n')
    handle.write.assert_any_call(docstring)
