from dataclasses import fields, dataclass, is_dataclass
from typing import Union
from uuid import UUID
from datetime import datetime

from psycopg2.extensions import cursor, connection

from utls import get_all_dataclass_fields
from utls import QueryBuilder


@dataclass
class Attributes:
    def load(self, input_data: dict):
        for key in input_data.keys():
            setattr(self, key, input_data[key])

    def __setattr__(self, key, value):
        if key in get_all_dataclass_fields(self):
            object.__setattr__(self, key, value)
        else:
            e = AttributeError(f"Attribute \"{key}\" not allowed for class \"{type(self).__name__}\"")
            raise e

    def dict(self):
        result = {}
        for key in get_all_dataclass_fields(self):
            result[key] = getattr(self, key)
        return result


class Object:
    id: UUID
    type: str
    attributes: Attributes

    def dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'attributes': self.attributes.dict()
        }


class Tag(Object):
    def __init__(self):
        super().__init__()
        self.type = 'tag'


class MangaAttr(Attributes):
    title: Union[dict, str] = None
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

    def __init__(self, manga_id=None):
        super().__init__()


class Manga(Object):
    relationships: list[dict]

    def __init__(self, manga_id=None):
        super().__init__()
        self.id = manga_id
        self.type = 'manga'
        self.attributes: MangaAttr = MangaAttr(self.id)

    def load(self, input_dict: dict):
        self.id = input_dict['id']
        self.attributes.load(input_dict['attributes'])

    def insert(self, cur):
        pass

    @staticmethod
    def select(cur: cursor, conn: connection = None):
        sql = QueryBuilder.Table('manga').join('\"manga_altTitle\"', 'id', 'manga_id').join('\"manga_title\"', 'id', 'manga_id')
        sql.prepare().select('id').text_has('title', 'Kaguya')
        cur.execute(sql.query, sql.data)
        result = cur.fetchall()
        return result

    def select_json(self, condition: Union[dict, str], omit_null=False):
        pass
