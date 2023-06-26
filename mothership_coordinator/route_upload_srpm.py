from typing import Annotated
from base64 import b64encode, b64decode
from json import loads

import rekor_sdk

from fastapi import APIRouter, Form, File, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mothership.models.entry import Entry

router = APIRouter(prefix="/upload_srpm")


@router.post("/", response_model=Entry)
async def upload_srpm(
    file: Annotated[bytes, File()],
    os_release: Annotated[str, Form()],
    req: Request,
) -> Entry:
    entry = {
        "kind": "rpm",
        "apiVersion": "0.0.1",
        "spec": {
            "package": {"content": b64encode(file).decode()},
            "publicKey": {"content": req.app.state.public_key},
        },
    }

    try:
        res: rekor_sdk.LogEntry = req.app.state.entries_api.create_log_entry(entry)
    except rekor_sdk.rest.ApiException as exc:
        err = loads(exc.body.decode())
        raise HTTPException(status_code=400, detail=err["message"])

    # Entry uuid is the key
    entry_uuid: str = list(res.keys())[0]

    # Res should have one value
    val: dict = list(res.values())[0]

    # Get base64 encoded RPM body
    body = loads(b64decode(val.get("body")).decode())

    # From body get the headers (spec.package.headers)
    headers = body.get("spec").get("package").get("headers")

    # Get the name, version, release, and epoch from the headers
    name = headers.get("Name")
    version = headers.get("Version")
    release = headers.get("Release")
    epoch = headers.get("Epoch")

    entry_db = Entry(
        id=None,
        entry_uuid=entry_uuid,
        package_name=name,
        package_version=version,
        package_release=release,
        package_epoch=epoch,
        os_release=os_release,
    )

    async with AsyncSession(req.app.state.db, expire_on_commit=False) as session:
        session.add(entry_db)
        await session.commit()

    return entry_db
