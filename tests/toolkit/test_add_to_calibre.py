import os
from pytest_mock import MockerFixture
from toolkit import add


def test_add(mocker: MockerFixture):
    metadata = {
        'title': 'Lorem',
        'author': 'Ipsum',
        'languages': ['English', 'French'],
        'publisher': 'Dolor',
        'tags': ['Tag1', 'Tag2']
    }

    mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('json.load', return_value=metadata)
    ms = mocker.patch('os.system')

    add('.')
    path = os.path.join('.', 'Lorem.md')
    image = os.path.join('.', 'cover.jpg')
    # noinspection SpellCheckingInspection
    ms.assert_called_once_with(f'calibredb add -a Ipsum -c {image} -l English,French -T Tag1,Tag2 -t Lorem {path}')
