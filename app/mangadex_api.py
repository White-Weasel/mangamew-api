import json

import requests
from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from app import app


def get_all_query_params(req: Request) -> dict:
    pass


@app.get('/{req_path:path}')
async def test_path(req_path: str, req: Request, response: Response):
    try:
        url = fr"https://api.mangadex.org/{req_path}?{str(req.query_params)}"
        result = requests.get(url)
        if 'json' in result.headers['content-type']:
            response.status_code = result.status_code
            return result.json()
        else:
            return {'error': 'You are trying to read non-json content-type which we are currently not supporting'}
    except Exception as e:
        return {'error': str(e)}

"""
@app.post('/{req_path:path}')
async def test_path(req_path: str, req: Request, response: Response):
    try:
        url = fr"https://api.mangadex.org/{req_path}"
        data = json.dumps(await req.json())
        result = requests.post(url, data=data)
        if 'json' in result.headers['content-type']:
            response.status_code = result.status_code
            return result.json()
        else:
            return HTMLResponse(result.content)
    except Exception as e:
        return {'error': str(e)}
"""
