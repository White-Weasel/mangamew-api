import uvicorn
import app
import os

app = app.app
try:
    DATABASE_URL = os.environ['DATABASE_URL']
except KeyError as e:
    uvicorn.run(app)
