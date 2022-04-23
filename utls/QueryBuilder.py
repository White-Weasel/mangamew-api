from dataclasses import fields, is_dataclass
from typing import Union, Protocol, Dict
from functools import partial

from models.Manga import Manga
from . import get_all_dataclass_fields, get_all_dataclass_data


class NoTableFound(Exception):
    pass


class IsDataclass(Protocol):
    # Checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


def replace_last(s: str, old, new):
    len_ = len(old)
    pos = s.rfind(old)
    return s[:pos] + new + s[pos + len_:]


class QueryBuilder:
    _table = ''
    function_ = ''
    query = ''
    _operation = ''
    _where_clause = ''
    _after_where = ''
    _join = ''
    __preparing = False
    data = []

    def prepare(self):
        self.__preparing = True
        return self

    def call_func(self, func_name: str, args: Union[list, tuple]):
        assert self._table == ''
        assert self._operation == ''
        tmp = f'SELECT {func_name}('
        for arg in args:
            if self.__preparing:
                tmp += ' %s,'
                self.data.append(arg)
            else:
                tmp += f' \'{arg},\''
        tmp = tmp[:-1]
        tmp += ')'
        self._operation = tmp
        pass

    def select(self, *args):
        assert self._table != ''
        tmp = 'SELECT '
        for col in args:
            tmp += col + ', '
        tmp = tmp[:-2]
        tmp += ' FROM '
        self._operation = tmp
        return self

    def count(self, column: str):
        assert self._table != ''
        self._operation = f'SELECT COUNT({column}) FROM '
        return self

    def where(self, condition: Union[dict, str, IsDataclass], omit_null=False):
        assert self._operation != '', "Where can not be on top"
        assert len(condition) > 0, "No condition passed"
        tmp = ' WHERE '

        if type(condition) is dict:
            for col, val in condition.items():
                if not omit_null or (omit_null and val is not None):
                    if self.__preparing:
                        tmp += f'{col}=%s AND '
                        self.data.append(val)
                    else:
                        tmp += f'{col}={val} AND '
            tmp = tmp[:-5]

        elif type(condition) is str:
            assert not self.__preparing, f"Cannot use pure string while preparing"
            tmp += condition

        elif is_dataclass(condition):
            for att in fields(condition):
                col = att.name
                val = getattr(condition, att.name)
                if not omit_null or (omit_null and val is not None):
                    if self.__preparing:
                        tmp += f'{col}=%s AND '
                        self.data.append(val)
                    else:
                        tmp += f'{col}={val} AND '

        else:
            raise TypeError(f"condition can not be of type {condition.__class__.__name__}")
        self._where_clause += tmp
        return self

    def and_(self, *args, **kwargs):
        self.where(*args, **kwargs)
        self._where_clause = replace_last(self._where_clause, 'WHERE', 'AND')

    def text_has(self, col, key):
        assert len(self._table) > 0
        if 'WHERE' not in self._where_clause:
            tmp = f' WHERE '
        else:
            tmp = f' AND '
        if self.__preparing:
            tmp += f'position(%s in {col})<>0 '
            self.data.append(key)
        else:
            tmp += f'{col} LIKE \'%{key}%\' '
        self._where_clause += tmp
        return self

    def order_by(self, *args, order: str = None):
        assert len(args) > 0
        assert self._table != ''
        tmp = ''
        order = order.upper()
        for col in args:
            tmp += f' ORDER BY {col} '
            if order is not None and (order == 'ASC' or order == 'DESC'):
                tmp += order
        self._after_where += tmp
        return self

    def group_by(self, *args):
        assert len(self._table) > 0
        tmp = ''
        for col in args:
            tmp += f' GROUP BY {col} '
        self._after_where += tmp
        return self

    def offset(self, offset: int):
        assert len(self._table) > 0
        self._after_where += f" OFFSET {offset}"
        return self

    def limit(self, limit: int):
        assert len(self._table) > 0
        self._after_where += f" LIMIT {limit} "
        return self

    def insert(self, data: Union[dict]):
        assert self._table != ''
        tmp = f'INSERT INTO {self._table} ('
        if type(data) is dict:
            getAlCol = data.keys
            getAllVal = data.values
        elif is_dataclass(data):
            getAlCol = partial(get_all_dataclass_fields, data)
            getAllVal = partial(get_all_dataclass_data, data)
        else:
            raise TypeError(f"data can not be of type {type(data)}")

        for col in getAlCol():
            tmp += f"{col}, "
        tmp = tmp[:-2] + ') VALUE ('

        for val in getAllVal():
            if self.__preparing:
                tmp += '%s, '
                self.data.append(val)
            else:
                tmp += f"'{val}', "
        tmp = tmp[:-2] + ')'

        self._operation = tmp
        return self

    def __repr__(self):
        self.query = self._operation + self._table + self._join + self._where_clause + self._after_where
        return self.query

    def __getattr__(self, item):
        return item


class Table(QueryBuilder):
    def __init__(self, table_name: str):
        super().__init__()
        if type(table_name) is str and table_name != '':
            self._table = table_name

    def join(self, join_table, col, join_col):
        tmp = f' JOIN {join_table} ON {self._table}.{col} = {join_table}.{join_col} '
        self._join += tmp
        return self


class Function:
    pass


class MangaJson(Table):
    def __init__(self):
        super().__init__('manga')
        self._operation = "SELECT jsonb_build_object( " \
                          "    'data', array_agg(public.get_manga_json_from_id(manga.id)), " \
                          "    'total', count(manga.id)) " \
                          "FROM "
