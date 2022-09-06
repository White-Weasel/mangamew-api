from typing import Optional, List
from uuid import UUID

from fastapi import Query, Depends

from app import app
from app.urls import orderParam, connect
from utls import QueryBuilder


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
                     order: Optional[dict[str, str]] = Depends(orderParam)
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
