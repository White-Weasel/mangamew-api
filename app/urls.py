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


from app.end_points.manga import *
from app.end_points.statistics import *


# noinspection PyUnusedLocal
@app.get('/author')
async def author(response: Response, ids: List[UUID] = Query(None)):
    # TODO
    return {'error': "this endpoint is currently unavailable"}


