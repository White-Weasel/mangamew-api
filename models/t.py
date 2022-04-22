import dataclasses
from datetime import datetime
from typing import Callable

from models.Manga import Tag, Attributes


@dataclasses.dataclass
class MangaAttr(Attributes):
    title: dict = None
    altTitles: list[dict] = None
    description: dict = None
    links: dict = None
    originalLanguage: str = None
    lastVolume: str = None
    lastChapter: str = None
    publicationDemographic: str = None
    status: str = None
    year: int = None
    contentRating: str = None
    tags: list[Tag] = None
    state: str = None
    createdAt: datetime = None
    updatedAt: datetime = None
    availableTranslatedLanguages: list[str] = None

    def __setattr__(self, key, value):
        assert hasattr(self, key), f"no attribute named {key}"
        self.__setattr__(key, value)

    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    t = MangaAttr()
    i = {'title': 1, 'tags': 2}
    t.load(i)
    pass
