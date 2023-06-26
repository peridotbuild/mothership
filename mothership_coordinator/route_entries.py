from typing import TypeVar, Generic
from dataclasses import asdict
from json import loads
from base64 import b64decode

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import rekor_sdk

from mothership.models.entry import Entry

router = APIRouter(prefix="/entries")

T = TypeVar("T")


class Pagination(Page[T], Generic[T]):
    class Config:
        allow_population_by_field_name = True
        fields = {"items": {"alias": "entries"}}


class DetailedEntry(BaseModel):
    entry: Entry
    rekor_entry: dict


def paginate_entries(session, params):
    return paginate(session.query(Entry), params=params)


# This method has a lot of hacky stuff, maybe SQLAlchemy was a mistake.
# I miss Tortoise
@router.get("/", response_model=Pagination[Entry], response_model_exclude_none=True)
async def get_entries(req: Request, params: Params = Depends()):
    async with AsyncSession(req.app.state.db) as session:
        page = await session.run_sync(paginate_entries, params=params)
        # Convert items to dict
        page.items = [asdict(item) for item in page.items]
        # Delete ID field
        for item in page.items:
            del item["id"]
        return JSONResponse(content=page.dict())


@router.get("/{entry_id}", response_class=DetailedEntry)
async def get_entry(req: Request, entry_id: str):
    async with AsyncSession(req.app.state.db) as session:
        result = await session.execute(
            select(Entry).where(Entry.entry_uuid == entry_id)
        )
        entry = result.scalars().first()

        # Fetch entry from Rekor
        try:
            res = req.app.state.entries_api.get_log_entry_by_uuid(entry_id)

            # Get first value
            val = list(res.values())[0]

            # Get base64 encoded RPM body
            body = loads(b64decode(val.get("body")).decode())

            entry_dict = asdict(entry)
            del entry_dict["id"]

            return JSONResponse(
                content={
                    "entry": entry_dict,
                    "rekor_entry": body,
                },
            )
        except rekor_sdk.rest.ApiException as exc:
            err = loads(exc.body.decode())
            raise HTTPException(status_code=400, detail=err.get("message")) from exc
