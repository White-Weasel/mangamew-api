import uvicorn
import app
import os

app = app.app
"""try:
    DATABASE_URL = os.environ['DATABASE_URL']
except KeyError as e:
    uvicorn.run(app)
"""
if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
