from fastapi import FastAPI
from urllib.parse import urlparse

app = FastAPI()

from . import urls
