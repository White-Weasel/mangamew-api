import json

import requests
from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from app import app


@app.get('/{req_path:path}')
async def get_proxy(req_path: str, req: Request, response: Response):
    try:
        url = fr"https://api.mangadex.org/{req_path}?{str(req.query_params)}"
        header = dict(req.headers)
        header['host'] = 'api.mangadex.org'
        result = requests.get(url, headers=header)
        if 'json' in result.headers['content-type']:
            response.status_code = result.status_code
            return result.json()
        else:
            # return {'error': 'You are trying to read non-json content-type which we are currently not supporting'}
            response.headers['location'] = r'https://api.mangadex.org/docs.html'
            return HTMLResponse(result.content)
    except Exception as e:
        return {'error': str(e)}


@app.post('/{req_path:path}')
async def test_path(req_path: str, req: Request, response: Response):
    try:
        url = fr"https://api.mangadex.org/{req_path}"
        data = json.dumps(await req.json())
        header = dict(req.headers)
        header['host'] = 'api.mangadex.org'
        header['Content-Type'] = r'application/json'
        result = requests.post(url, data=data, headers=header)
        if 'json' in result.headers['content-type']:
            response.status_code = result.status_code
            return result.json()
        else:
            return HTMLResponse(result.content)
    except Exception as e:
        return {'error': str(e)}


@app.delete('/{req_path:path}')
async def test_path(req_path: str, req: Request, response: Response):
    try:
        url = fr"https://api.mangadex.org/{req_path}"
        # data = json.dumps(await req.json())
        header = dict(req.headers)
        header['host'] = 'api.mangadex.org'
        header['Content-Type'] = r'application/json'
        result = requests.delete(url, headers=header)
        if 'json' in result.headers['content-type']:
            response.status_code = result.status_code
            return result.json()
        else:
            return HTMLResponse(result.content)
    except Exception as e:
        return {'error': str(e)}
