from textwrap import dedent
from common import Type, NovelData


def data(content: str):
    return NovelData(Type.UNRECOGNIZED, content)


def format_csv(csv):
    return dedent(csv).strip()
