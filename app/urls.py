from uuid import UUID

from fastapi import Query, Response
from starlette.responses import RedirectResponse

from app import app
import psycopg2
from typing import List, Optional
import os

from models.Manga import Manga
from utls import QueryBuilder

try:
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
except KeyError as e:
    print("we are running offline")
    conn = psycopg2.connect(service='mangamew_api_service')


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
    return {'data': result, 'total': len_}


@app.get('/manga')
async def manga(response: Response, ids: Optional[List[UUID]] = Query(None), title: Optional[str] = None):
    if len(ids) > 0:
        result = []
        cur = conn.cursor()
        for mid in ids:
            cur.callproc('get_manga_json_from_id', (str(mid),))
            result += cur.fetchall()[0]
        response.headers["access-control-allow-origin"] = r"https://mangamew.vercel.app"
        return {'data': result, 'total': len(result)}


@app.get('/author')
async def author(ids: List[UUID] = Query(None)):
    pass
