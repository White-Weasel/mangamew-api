from uuid import UUID

from fastapi import Query

from app import app
import psycopg2
from typing import List, Optional
import os


try:
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
except KeyError as e:
    print("we are running offline")
    conn = psycopg2.connect(service='mangamew_api_service')


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.get('/manga')
async def manga(ids: List[UUID] = Query(None)):
    if ids is None:
        return 'abc'
    else:
        result = []
        cur = conn.cursor()
        for mid in ids:
            cur.callproc('get_manga_json_from_id', (str(mid),))
            result += cur.fetchall()[0]
        return {'data': result, 'total': len(result)}


@app.get('/author')
async def author(ids: List[UUID] = Query(None)):
    pass
