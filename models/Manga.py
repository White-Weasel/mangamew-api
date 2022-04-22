from uuid import UUID
from datetime import datetime


class Attributes:
    def load(self, input_data: dict):
        for key in input_data.keys():
            if hasattr(self, key):
                setattr(self, key, input_data[key])


class Object:
    id: UUID
    type: str
    attributes: Attributes


class Tag(Object):
    def __init__(self):
        super().__init__()


class MangaAttr(Attributes):
    title: dict
    altTitles: list[dict]
    description: dict
    links: dict
    originalLanguage: str
    lastVolume: str
    lastChapter: str
    publicationDemographic: str
    status: str
    year: int
    contentRating: str
    tags: list[Tag]
    state: str
    createdAt: datetime
    updatedAt: datetime
    availableTranslatedLanguages: list[str]

    def __init__(self):
        super().__init__()


class Manga(Object):
    relationships: list[dict]

    def __init__(self, manga_id=None):
        super().__init__()
        self.id = manga_id
        self.type = 'manga'
        if self.id is not None:
            self.attributes: MangaAttr = MangaAttr()

    def load(self, input_dict: dict):
        self.id = input_dict['id']
        self.attributes.load(input_dict['attributes'])
