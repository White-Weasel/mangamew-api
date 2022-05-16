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

psycopg2.extras.register_uuid()


def dict_param(req: Request) -> dict:
    data = {}
    try:
        _query = dict((k, v) for k, v in req.query_params.items())
        for _k in _query.keys():
            dict_key = str(_k).replace('[', ' ').replace(']', ' ').split()
            if len(dict_key) > 1:
                dict_ = dict_key[0]
                key = dict_key[1]
                val = _query.get(_k)

                try:
                    d = data[dict_]
                except KeyError:
                    data[dict_] = {}
                    d = data[dict_]
                d[key] = val
            else:
                continue
    except Exception as e:
        print(e)
    finally:
        return data


def orderParam(req: Request):
    return dict_param(req).get('order')


def connect():
    try:
        DATABASE_URL = os.environ['DATABASE_URL']

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    except KeyError:
        print("we are running offline")
        conn = psycopg2.connect(service='mangadex_clone_service')

    return conn


def call_sql_function(cur: psycopg2.extensions.cursor, function_name, data):
    cur.callproc(function_name, data)
    return cur.fetchall()[0]


@app.get('/')
async def root():
    return RedirectResponse(url='/docs')


@app.get('/manga')
async def manga_list(ids: Optional[list[UUID]] = Query(None, alias='ids[]'),
                     title: Optional[str] = None,
                     includedTags: Optional[List[UUID]] = Query(None, alias='includedTags[]'),
                     includedTagsMode: Optional[str] = 'and',
                     excludedTags: Optional[list[UUID]] = Query(None, alias='excludedTags[]'),
                     publicationDemographic: Optional[List[str]] = Query(None, alias='publicationDemographic[]'),
                     year: Optional[int] = Query(None),
                     originalLanguage: Optional[list[str]] = Query(None, alias='originalLanguage[]'),
                     excludedOriginalLanguage: Optional[list[str]] = Query(None, alias='excludedOriginalLanguage[]'),
                     authors: Optional[list[UUID]] = Query(None, alias='authors[]'),
                     artists: Optional[list[UUID]] = Query(None, alias='artists[]'),
                     availableTranslatedLanguage: Optional[list[str]] = Query(None,
                                                                              alias='availableTranslatedLanguage[]'),
                     limit: Optional[int] = 10,
                     contentRating: Optional[list[str]] = Query(None, alias='contentRating[]'),
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
    if excludedTags is not None:
        manga_sql.exclude_tags(excludedTags)
    if year is not None:
        manga_sql.where('year = %s', year)
    if originalLanguage is not None:
        manga_sql.where('"originalLanguage" = ANY(%s)', originalLanguage)
    if excludedOriginalLanguage is not None:
        manga_sql.where('NOT("originalLanguage" = ANY(%s))', excludedOriginalLanguage)
    if contentRating is not None:
        manga_sql.where('"contentRating" = ANY(%s)', contentRating)
    if availableTranslatedLanguage is not None:
        manga_sql.has_translated_language(availableTranslatedLanguage)
    if order is not None:
        manga_sql.order_by(order)
    if publicationDemographic is not None:
        manga_sql.has_demographics(publicationDemographic)
    if authors is not None:
        manga_sql.has_author(authors)
    if artists is not None:
        manga_sql.has_artist(artists)

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


# noinspection PyUnusedLocal
@app.get('/author')
async def author(response: Response, ids: List[UUID] = Query(None)):
    # TODO
    return {'error': "this endpoint is currently unavailable"}


@app.get('/statistics/manga')
async def mangas_statistics(manga: List[UUID] = Query(None, alias='manga[]')):
    result = {}
    if len(manga) > 0:
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('select id, rating, "followedCount" as "follows" from manga WHERE id = ANY(%s)', (manga,))
        re = cur.fetchall()
        for row in re:
            # noinspection PyTypeChecker
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
