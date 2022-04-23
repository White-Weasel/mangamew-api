from dataclasses import fields, dataclass
from datetime import datetime
from typing import Callable

from models.Manga import Manga

if __name__ == '__main__':
    t = Manga()
    i = {'id': 123,
         'attributes': {'title': 1, 'year': 2}}
    t.load(i)
    pass
