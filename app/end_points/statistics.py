from app.urls import *


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
