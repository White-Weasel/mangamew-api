from uuid import UUID

from fastapi import Query, Response
from starlette.responses import RedirectResponse

from app import app
import psycopg2
import psycopg2.extras
from psycopg2.extensions import cursor
from typing import List, Optional
import os
from utls import QueryBuilder

try:
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
except KeyError as e:
    print("we are running offline")
    conn = psycopg2.connect(service='mangadex_clone_service')

psycopg2.extras.register_uuid()


def call_sql_function(cur: psycopg2.extensions.cursor, function_name, data):
    cur.callproc(function_name, data)
    return cur.fetchall()[0]


@app.get('/')
async def root():
    response = RedirectResponse(url='/docs')
    return response


@app.get('/manga/{manga_id}')
async def manga_by_id(manga_id: UUID, response: Response):
    cur = conn.cursor()
    cur.callproc('get_manga_json_from_id', (manga_id,))
    result = cur.fetchall()[0]
    len_ = 0
    if result is not None:
        len_ = len(result)
    response.headers["access-control-allow-origin"] = r"https://mangamew.vercel.app"
    cur.close()
    return {'_data': result, 'total': len_}


@app.get('/manga')
async def manga_list(response: Response, ids: Optional[UUID] = None, title: Optional[str] = None,
                     includedTags: Optional[list[UUID]] = Query(None), includedTagsMode: Optional[str] = 'and',
                     limit: Optional[int] = 10, offset: Optional[int] = 0):
    manga_sql = QueryBuilder.MangaQuery().limit(limit).offset(offset)
    if ids is not None:
        manga_sql.has_id(ids)
    if title is not None:
        manga_sql.title_has(title)
    if len(includedTags) > 0:
        if includedTagsMode.lower() == 'and':
            manga_sql.has_all_tags(includedTags)

    manga_sql = QueryBuilder.MangaJsonQuery(manga_sql)
    cur = conn.cursor()
    cur.execute(manga_sql.query, manga_sql.data)
    result = cur.fetchall()[0][0]
    cur.close()

    response.headers["access-control-allow-origin"] = r"https://mangamew.vercel.app"
    return result


@app.get('/author')
async def author(response: Response, ids: List[UUID] = Query(None)):
    pass


@app.get('/statistics/manga')
async def mangas_statistics(response: Response, manga: List[UUID] = Query(None)):
    result = {}
    if len(manga) > 0:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM manga_statistics WHERE manga_id = ANY(%s)', (manga,))
        re = cur.fetchall()
        for row in re:
            result[str(row['manga_id'])] = {'rating': {'average': row['rating']}, 'follows': row['follows']}
        pass

        cur.close()
    response.headers["access-control-allow-origin"] = r"https://mangamew.vercel.app"
    return result


@app.get('/statistics/manga/{manga_uuid}')
async def manga_statistics(response: Response, manga_uuid: UUID):
    # FIXME
    result = await mangas_statistics(response, [manga_uuid, ])
    return result
