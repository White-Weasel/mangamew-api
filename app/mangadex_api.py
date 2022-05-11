import requests

from app import app


@app.get('/{req_path:path}')
async def test_path(req_path: str):
    try:
        result = requests.get(fr"https://api.mangadex.org/{req_path}")
        if 'json' in result.headers['content-type']:
            return result.json()
        else:
            return {'error': 'You are trying to read non-json content-type which we are currently not supporting'}
    except Exception as e:
        return {'error': str(e)}
