from contextlib import asynccontextmanager
from base64 import b64encode

from fastapi import FastAPI
from fastapi_pagination import add_pagination

import rekor_sdk

from mothership.db import new_engine
from mothership_coordinator.route_upload_srpm import router as upload_srpm_router
from mothership_coordinator.route_entries import router as entries_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    rekor_conf = rekor_sdk.Configuration()
    rekor_conf.host = "http://localhost:3000"
    entries_api = rekor_sdk.EntriesApi(rekor_sdk.ApiClient(rekor_conf))
    app.state.entries_api = entries_api

    with open("data/rh_public_key.asc", "rb") as f:
        app.state.public_key = b64encode(f.read()).decode()

    engine = new_engine()
    app.state.db = engine
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(upload_srpm_router)
app.include_router(entries_router)

add_pagination(app)
