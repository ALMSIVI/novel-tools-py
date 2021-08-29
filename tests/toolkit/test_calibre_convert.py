import os
from pytest_mock import MockerFixture
from toolkit import convert


def test_convert(mocker: MockerFixture):
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

    convert('.')
    path = os.path.join('.', 'Lorem')
    image = os.path.join('.', 'cover.jpg')
    ms.assert_called_once_with(f'ebook-convert {path}.md {path}.epub --level1-toc //h:h1 --level2-toc //h:h2 '
                               f'--level3-toc //h:h3 --authors Ipsum --cover {image} --language English,French '
                               '--publisher Dolor --tags Tag1,Tag2 --title Lorem')
