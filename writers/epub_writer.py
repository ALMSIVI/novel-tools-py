from datetime import datetime
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
from ebooklib import epub
from markdown import markdown
from common import FieldMetadata, NovelData
from .__structure_writer import StructureWriter, Structure
from utils import purify_name


class EpubWriter(StructureWriter):
    """
    Generates a epub file for the book. An epub is essentially a zip file consisting of html files, stylesheets, and
    multimedia (including images). Compared to plaintext files (txt/md), it allows custom styles and illustrations
    bundled together.

    The epub specification requires title, language and identifier metadata. Therefore, a BOOK_TITLE must be included
    with language and id in its `others` field. You can do that with MetadataReader.

    The created epub will contain a cover page (if a cover is specified), and a metadata page that contains all the
    metadata plus the book introduction. It will also contain one page for each volume and chapter. You can customize
    the page layouts by specifying the html template.

    For better style customization, the tag for each NovelData will be used as html classes. Please ensure you
    use a `CsvWriter` to store the structure and have `tag` in `additional_fields`.

    In the generated html, the titles (book/volume/chapter) will surrounded with the <h1> tag. The metadata will
    be surrounded with the <span> tag, and will use its name as id. The introductions (book/volume) and the chapter
    contents will be converted into html as markdown, and then the classes will be inserted accordingly.

    TODO add illustration support
    """

    @staticmethod
    def required_fields() -> list[FieldMetadata]:
        return StructureWriter.required_fields() + [
            FieldMetadata('in_dir', 'Path',
                          description='The directory that stores all the additional data, including '
                                      'stylesheets and/or images.'),
            FieldMetadata('encoding', 'str', default='utf-8',
                          description='Encoding of the metadata template file.'),
            FieldMetadata('include_nav', 'bool', default=False,
                          description='Whether a TOC will be placed after the cover page.'),
            FieldMetadata('stylesheet', 'str', optional=True,
                          description='The stylesheet for the book. If it is not specified, a default one will be '
                                      'used.'),
            FieldMetadata('cover', 'str', default='cover.jpg',
                          description='Cover image for the book. If it exists, a cover page will be added.'),
            FieldMetadata('cover_title', 'str', default='Cover',
                          description='Title for the cover page. Useful for localization.'),
            FieldMetadata('metadata_template', 'str', optional=True,
                          description='The template for the metadata page. If it is not specified, a default one will '
                                      'be used.'),
            FieldMetadata('metadata_title', 'str', default='Metadata',
                          description='Title for the metadata page. Useful for localization.'),
            FieldMetadata('author_separator', 'str', default=', ',
                          description='Separator for multiple authors on the metadata page.'),
            FieldMetadata('date_format', 'str', default='%B %Y',
                          description='Format for the data on the metadata page. For mor information, check the '
                                      'documentation for datetime.'),
            FieldMetadata('volume_template', 'str', optional=True,
                          description='The template for the volume page. If it is not specified, a default one will be'
                                      ' used.'),
            FieldMetadata('chapter_template', 'str', optional=True,
                          description='The template for the chapter page. If it is not specified, a default one will be'
                                      ' used.')
        ]

    def __init__(self, args):
        args = self.extract_fields(args)
        super().__init__(args)
        self.in_dir: Path = args['in_dir']
        self.encoding = args['encoding']
        self.include_nav = args['include_nav']
        self.cover = args['cover']
        self.cover_title = args['cover_title']
        self.metadata_title = args['metadata_title']
        self.author_separator = args['author_separator']
        self.date_format = args['date_format']

        # Stylesheet and metadata templates will only be used once, so we don't store them inside the class
        self.stylesheet = self.in_dir / args['stylesheet'] if 'stylesheet' in args \
            else Path('config', 'epub', 'stylesheet.css')

        self.metadata_template = self.in_dir / args['metadata_template'] if 'metadata_template' in args \
            else Path('config', 'epub', 'metadata_page.html')

        # Volume and chapter templates will be reused, so we store them to save I/O operations.
        volume_template = self.in_dir / args['volume_template'] if 'volume_template' in args \
            else Path('config', 'epub', 'volume_page.html')
        with volume_template.open('rt', encoding=self.encoding) as f:
            self.volume_template = f.read()

        chapter_template = self.in_dir / args['chapter_template'] if 'chapter_template' in args \
            else Path('config', 'epub', 'chapter_page.html')
        with chapter_template.open('rt', encoding=self.encoding) as f:
            self.chapter_template = f.read()

    def write(self) -> None:
        book = epub.EpubBook()
        self.__write_metadata(book)
        cover_page = self.__create_cover_page(book)
        book.add_item(cover_page)

        css = self.__create_stylesheet()
        book.add_item(css)

        metadata_page = self.__create_metadata_page()
        book.add_item(metadata_page)

        toc = [cover_page, metadata_page]
        spine = [cover_page, 'nav', metadata_page] if self.include_nav else [cover_page, metadata_page]

        if self.has_volumes:
            for volume in self.structure.children:
                volume_page, chapter_pages = self.__create_volume_page(volume)
                book.add_item(volume_page)
                spine.append(volume_page)
                toc.append((epub.Section(volume_page.title, href=volume_page.file_name), chapter_pages))
                for chapter_page in chapter_pages:
                    book.add_item(chapter_page)
                    spine.append(chapter_page)
        else:
            for chapter in self.structure.children:
                chapter_page = self.__create_chapter_page(chapter)
                book.add_item(chapter_page)
                toc.append(chapter_page)
                spine.append(chapter_page)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.toc = toc
        book.spine = spine
        path = self.out_dir / purify_name(self._get_filename(self.structure.title) + '.epub')
        epub.write_epub(path, book)

    def __write_metadata(self, book: epub.EpubBook):
        """Writes metadata into the epub book. You can look up supported metadata in `config/sample_metadata.json`."""

        book_title = self.structure.title

        # Required
        if title := self._get_content(book_title):
            book.set_title(title)
        else:
            raise ValueError('Book must contain a title.')

        if identifier := book_title.get('id'):
            book.set_identifier(identifier)
        else:
            raise ValueError('Book must contain an identifier.')

        languages = book_title.get('languages')
        if languages and len(languages) > 0:
            for language in languages:
                book.set_language(language)
        else:
            raise ValueError('Book must contain at least one language.')

        # Optional
        authors = book_title.get('authors')
        if authors:
            for author in book_title.get('authors'):
                book.add_author(author)

        for tag in book_title.get('tags'):
            book.add_metadata('DC', 'subject', tag)

        if publisher := book_title.get('publisher'):
            book.add_metadata('DC', 'publisher', publisher)

        if date := book_title.get('date'):
            book.add_metadata('DC', 'date', datetime.fromisoformat(date).isoformat())

    def __create_stylesheet(self) -> epub.EpubItem:
        css = epub.EpubItem(uid='style', file_name='Styles/stylesheet.css', media_type='text/css')
        with self.stylesheet.open('rt', encoding=self.encoding) as f:
            css.set_content(f.read())
        return css

    def __create_cover_page(self, book: epub.EpubBook) -> Optional[epub.EpubHtml]:
        """
        We will not be using `EpubBook.set_cover()` here, because it will set the cover page to `linear="no"` in the
        spine. This means the page will not be ordered correctly.
        """
        cover_path = self.in_dir / self.cover
        if cover_path.is_file():
            cover_image = epub.EpubCover(file_name=f'Images/{self.cover}')
            book.add_item(cover_image)

            with cover_path.open('rb') as f:
                cover_image.set_content(f.read())

            page = epub.EpubHtml(uid='cover', file_name='cover.xhtml', title=self.cover_title)
            with Path('config', 'epub', 'cover_stylesheet.css').open('rt') as f:
                css = epub.EpubItem(uid='cover-style', file_name='Styles/cover-style.css', media_type='text/css',
                                    content=f.read())
                book.add_item(css)
                page.add_item(css)
            with Path('config', 'epub', 'cover_page.html').open('rt') as f:
                page.set_content(f.read().format(cover=self.cover))

            return page

    def __create_metadata_page(self) -> epub.EpubHtml:
        """
        Writes the metadata page to the book.

        Currently, supported metadata on the page include title, identifier, authors, publisher and date. Use {<name>}
        to include them on the metadata page. Also, use {introduction} for the book introduction.

        You need to specify your own classes and styles for the metadata. The introduction, on the other hand, will be
        handled by the Writer.
        """
        page = epub.EpubHtml(uid='metadata', title=self.metadata_title, file_name='Text/metadata.xhtml')
        book_title = self.structure.title
        with self.metadata_template.open('rt', encoding=self.encoding) as f:
            content = f.read().format(title=self.__format_title(book_title),
                                      identifier=self.__format_metadata('id', book_title.get('id')),
                                      authors=self.__format_metadata('authors', self.author_separator.join(
                                          book_title.get('authors'))),
                                      publisher=self.__format_metadata('publisher', book_title.get('publisher')),
                                      date=self.__format_metadata('date', datetime.fromisoformat(
                                          book_title.get('date')).strftime(self.date_format)),
                                      introduction='\n'.join(
                                          [self.__format_content(intro) for intro in self.structure.contents]))
        page.set_content(content)
        self.__add_stylesheet(page, False)
        return page

    def __create_volume_page(self, volume: Structure) -> tuple[epub.EpubHtml, list[epub.EpubHtml]]:
        """
        Writes a single volume, together with its chapters, to the book.

        For the volume template, use {title} and {introduction} as placeholders for the volume title and intro. For the
        chapter template, use {title} and {contents} as placeholders for the chapter title and content.
        """
        # Write volume page
        title = volume.title
        volume_filename = purify_name(self._get_filename(title))
        filename_text = f'Text/{volume_filename}/_intro.html'
        page = epub.EpubHtml(title=self._get_content(title), file_name=filename_text)
        content = self.volume_template.format(title=self.__format_title(title),
                                              introduction='\n'.join(
                                                  [self.__format_content(intro) for intro in volume.contents]))
        page.set_content(content)
        self.__add_stylesheet(page, True)

        chapters = [self.__create_chapter_page(chapter, volume_filename) for chapter in volume.children]
        return page, chapters

    def __create_chapter_page(self, chapter: Structure, volume_filename: Optional[str] = None) -> epub.EpubHtml:
        title = chapter.title
        chapter_filename = purify_name(self._get_filename(title))
        filename_text = f'Text/{volume_filename}/{chapter_filename}.html' \
            if volume_filename else f'Text/{chapter_filename}.html'
        page = epub.EpubHtml(title=self._get_content(title), file_name=filename_text)
        content = self.chapter_template.format(title=self.__format_title(title),
                                               contents='\n'.join(
                                                   [self.__format_content(content) for content in chapter.contents]))
        page.set_content(content)
        self.__add_stylesheet(page, volume_filename is not None)
        return page

    @staticmethod
    def __add_stylesheet(page: epub.EpubHtml, in_volume: bool):
        filename = '../../Styles/stylesheet.css' if in_volume else '../Styles/stylesheet.css'
        css = epub.EpubItem(file_name=filename, media_type='text/css')
        page.add_item(css)

    @staticmethod
    def __format_metadata(name: str, content: str) -> str:
        soup = BeautifulSoup()
        metadata = soup.new_tag('span')
        metadata['id'] = name
        metadata.string = content
        soup.append(metadata)
        return str(soup)

    def __format_title(self, data: NovelData) -> str:
        soup = BeautifulSoup()
        title = soup.new_tag('h1')
        title.string = self._get_content(data)
        if data.has('tag'):
            title['class'] = data.get('tag')
        soup.append(title)
        return str(soup)

    @staticmethod
    def __format_content(data: NovelData) -> str:
        content = data.content
        if not content:
            soup = BeautifulSoup()
            soup.append(soup.new_tag('br'))
        else:
            html = markdown(content)
            soup = BeautifulSoup(html, 'html.parser')

        if data.has('tag'):
            for child in soup.children:
                child['class'] = data.get('tag')

        # TODO: illustration
        return str(soup)
