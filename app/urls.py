from uuid import UUID

from fastapi import Query, Response, Request, Depends
from starlette.responses import RedirectResponse

from app import app
import psycopg2
import psycopg2.extras
from psycopg2.extensions import cursor
from typing import List, Optional, Dict
import os
from utls import QueryBuilder
from pydantic import BaseModel


def dict_param(req: Request) -> dict:
    data = {}
    try:
        _query = dict((k, v) for k, v in req.query_params.items())
        for _k in _query.keys():
            dict_key = str(_k).replace('[', ' ').replace(']', ' ').split()
            dict_ = dict_key[0]
            key = dict_key[1]
            val = _query.get(_k)

            try:
                d = data[dict_]
            except KeyError:
                data[dict_] = {}
                d = data[dict_]
            d[key] = val
    except Exception as e:
        print(e)
    finally:
        return data


def orderParam(req: Request):
    return dict_param(req).get('order')


@app.get('/test')
async def test_(order: dict = Depends(orderParam)):
    return order


def connect():
    try:
        DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    except KeyError:
        print("we are running offline")
        conn = psycopg2.connect(service='mangadex_clone_service')

    return conn


psycopg2.extras.register_uuid()


def call_sql_function(cur: psycopg2.extensions.cursor, function_name, data):
    cur.callproc(function_name, data)
    return cur.fetchall()[0]


@app.get('/')
async def root():
    response = RedirectResponse(url='/docs')
    return response


@app.get('/manga')
async def manga_list(ids: Optional[UUID] = Query(None, alias='ids[]'),
                     title: Optional[str] = None,
                     includedTags: Optional[List[UUID]] = Query(None, alias='includedTags[]'),
                     includedTagsMode: Optional[str] = 'and',
                     publicationDemographic: Optional[List[str]] = Query(None, alias='publicationDemographic[]'),
                     year: Optional[int] = Query(None),
                     limit: Optional[int] = 10,
                     offset: Optional[int] = 0,
                     order: Optional[Dict[str, str]] = Depends(orderParam)
                     ):
    manga_sql = QueryBuilder.MangaQuery().limit(limit).offset(offset)
    if ids is not None:
        manga_sql.has_id(ids)
    if title is not None:
        manga_sql.title_has(title)
    if includedTags is not None:
        if includedTagsMode.lower() == 'and':
            manga_sql.has_all_tags(includedTags)
    if year is not None:
        manga_sql.where('year = %s', year)
    if order is not None:
        manga_sql.order_by(order)
    if publicationDemographic is not None:
        manga_sql.has_demographics(publicationDemographic)

    manga_sql = QueryBuilder.MangaJsonQuery(manga_sql)

    conn = connect()
    cur = conn.cursor()
    cur.execute(manga_sql.query, manga_sql.data)
    result = cur.fetchall()[0][0]
    cur.close()
    conn.close()

    return result


@app.get('/manga/tag')
async def all_tag():
    conn = connect()
    cur = conn.cursor()
    cur.callproc('get_all_tags')
    result = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return result


@app.get('/manga/{manga_id}')
async def manga_by_id(manga_id: UUID):
    conn = connect()
    cur = conn.cursor()
    cur.callproc('get_manga_json_from_id', (manga_id,))
    result = cur.fetchall()[0]
    len_ = 0
    if result is not None:
        len_ = len(result)
    cur.close()
    conn.close()
    return {'_data': result, 'total': len_}


@app.get('/author')
async def author(response: Response, ids: List[UUID] = Query(None)):
    pass


@app.get('/statistics/manga')
async def mangas_statistics(manga: List[UUID] = Query(None)):
    result = {}
    if len(manga) > 0:
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('select id, rating, "followedCount" as "follows" from manga WHERE id = ANY(%s)', (manga,))
        re = cur.fetchall()
        for row in re:
            result[str(row['id'])] = {'rating': {'average': row['rating']}, 'follows': row['follows']}
        pass

        cur.close()
        conn.close()

    result = {'statistics': result}

    return result


@app.get('/statistics/manga/{manga_uuid}')
async def manga_statistics(manga_uuid: UUID):
    result = await mangas_statistics([manga_uuid, ])
    return result
