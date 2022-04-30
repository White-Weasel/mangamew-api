from typing import Union
from uuid import UUID


class SqlStatement(str):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WhereClauses:
    def __init__(self):
        pass


class JoinSubquery:
    query: str
    join_method: str
    join_condition: str
    name: str

    def __init__(self, query, name, join_condition: str, join_method: str = 'JOIN'):
        self.query = query
        self.join_method = join_method
        self.join_condition = join_condition
        self.name = name

    def __repr__(self):
        return f"{self.join_method} ({self.query}){self.name} ON {self.join_condition}"


class FromClause:
    tables: list[Union[str, JoinSubquery, 'QueryBuilder']]

    def __init__(self, tables: list[Union[str, JoinSubquery, 'MangaQuery']] = None):
        if tables is not None:
            self.tables = tables
        else:
            self.tables = []

    def add_clause(self, new_clause):
        self.tables.append(new_clause)
        return self

    def __repr__(self):
        result = ''
        for table in self.tables:
            result += f"{str(table)} "
        return result

    def __len__(self):
        return len(self.tables)

    def __add__(self, other):
        return self.add_clause(other)


class QueryBuilder:
    __query: str
    __where_clauses: list

    def __init__(self):
        self.data = []
        self.__query = ''


class MangaQuery:
    _query: str
    _data: list
    limit_: int
    offset_: int
    select_clause: list[str]
    from_clauses: FromClause
    where_clause: list[str]
    order_by_: dict

    def __init__(self):
        self.order_by_ = {}
        self.select_clause = ['manga.id']
        self.from_clauses = FromClause(['manga'])
        self.where_clause = []
        self._data = []
        self.limit_ = 10
        self.offset_ = 0

    def has_all_tags(self, tag_list: list):
        query = "select id from public.mangas_with_all_tags(%s)"
        tag_subquery = JoinSubquery(query=query, name='has_tag', join_condition='manga.id = has_tag.id',
                                    join_method='INNER JOIN')
        self.from_clauses.add_clause(tag_subquery)
        self.append_data(tag_list)
        return self

    def where(self, condion, data):
        self.append_data(data)
        self.where_clause.append(condion)
        return self

    def has_demographics(self, demos: list[str]):
        query = f'"publicationDemographic" = ANY(%s) '
        self.append_data(demos)
        self.where_clause.append(query)
        return self

    def title_has(self, key: str):
        query = "select id from public.manga_title_has(%s)"
        title_subquery = JoinSubquery(query=query, name='has_title', join_condition='manga.id = has_title.id',
                                      join_method="INNER JOIN")
        self.from_clauses.add_clause(title_subquery)
        self.append_data(key)
        return self

    def has_id(self, key_id: UUID):
        self.where_clause.append('manga.id = %s')
        self.append_data(key_id)
        return self

    def limit(self, limit):
        self.limit_ = limit
        return self

    def offset(self, offset):
        self.offset_ = offset
        return self

    def order_by(self, order: dict):
        self.order_by_ = order
        return self

    @property
    def query(self):
        result = f'SELECT '
        for sel in self.select_clause:
            result += f"{sel} "
        result += f'FROM {str(self.from_clauses)} '

        if len(self.where_clause) > 0:
            result += 'WHERE '
            for condition in self.where_clause:
                result += f"{str(condition)} AND "

            result = result[:-4]

        if len(self.order_by_) > 0:
            for col in self.order_by_:
                result += f"ORDER BY \"{col}\" {self.order_by_[col]} "

        result += f"LIMIT {self.limit_} "
        result += f"OFFSET {self.offset_} "
        return result

    @property
    def data(self):
        return self._data

    def append_data(self, new_data):
        self._data.append(new_data)

    def __repr__(self):
        return self.query


class MangaJsonQuery(MangaQuery):
    subquery: MangaQuery

    def __init__(self, subquery: MangaQuery = None):
        super().__init__()
        if subquery is not None:
            self.subquery = subquery
        else:
            self.subquery = MangaQuery()
        self.from_clauses = FromClause([self.subquery])

    @property
    def data(self):
        return self.subquery.data

    @property
    def query(self):
        sel = f"jsonb_build_object( " \
              f"      'data', array_agg(public.get_manga_json_from_id(id)), " \
              f"      'limit', {self.limit_}, " \
              f"      'offset', {self.offset_}, " \
              f"      'total', count(id) " \
              f") "
        result = f'SELECT {sel} '
        result += f'FROM ({str(self.from_clauses)})manga_id_subquery '
        if len(self.where_clause) > 0:
            result += 'WHERE '
            for condition in self.where_clause:
                result += f"{str(condition)} AND "

            result = result[:-4]
        result += f"LIMIT {self.limit_} "
        result += f"OFFSET {self.offset_} "
        return result
