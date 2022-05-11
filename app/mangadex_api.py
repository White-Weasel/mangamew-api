import requests
from fastapi import Request
from app import app


def get_all_query_params(req: Request) -> dict:
    pass


@app.get('/{req_path:path}')
async def test_path(req_path: str, req: Request):
    try:
        url = fr"https://api.mangadex.org/{req_path}?{str(req.query_params)}"
        result = requests.get(url)
        if 'json' in result.headers['content-type']:
            return result.json()
        else:
            return {'error': 'You are trying to read non-json content-type which we are currently not supporting'}
    except Exception as e:
        return {'error': str(e)}
