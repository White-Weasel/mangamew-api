from dataclasses import fields, is_dataclass
from typing import Union, Protocol, Dict
from functools import partial
from . import get_all_dataclass_fields, get_all_dataclass_data


class NoTableFound(Exception):
    pass


class IsDataclass(Protocol):
    # Checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


class QueryBuilder:
    table = ''
    function_ = ''
    query = ''
    __operation = ''
    __where_clause = ''
    __join = ''
    __preparing = False
    data = []

    def prepare(self):
        self.__preparing = True
        return self

    def call_func(self, func_name: str):
        # TODO
        pass

    def select(self, *args):
        assert self.table != ''
        self.query = 'SELECT '
        for col in args:
            self.query += col + ', '
        self.query = self.query[:-2]
        self.query += ' FROM ' + self.table
        return self

    def count(self, column: str):
        assert self.table != ''
        self.query = f'SELECT COUNT({column}) FROM {self.table} '
        return self

    def where(self, condition: Union[dict, str, IsDataclass], omit_null=False):
        assert self.query != '', "Where can not be on top"
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
        self.query += tmp
        return self

    def and_(self, condition: str):
        pass

    def insert(self, data: Union[dict]):
        assert self.table != ''
        self.query = f'INSERT INTO {self.table} ('
        tmp = ''
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

        self.query += tmp
        return self

    def __repr__(self):
        return self.query

    def __getattr__(self, item):
        return item


class Table(QueryBuilder):
    def __init__(self, table_name: str):
        super().__init__()
        if type(table_name) is str and table_name != '':
            self.table = table_name


class Function:
    pass
