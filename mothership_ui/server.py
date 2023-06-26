from typing import List
from json import dumps

import aiohttp
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

import pv2_ui_base
from mothership.models.entry import Entry
from mothership_coordinator.route_entries import DetailedEntry

from mothership_ui.utils import templates

app = FastAPI()

css_response = FileResponse(pv2_ui_base.get_css_min_path())


@app.get("/_/healthz")
def health():
    return {"status": "ok"}


@app.get("/pv2-ui/pv2.min.css", response_class=FileResponse)
def get_css():
    return css_response


@app.get("/favicon.ico")
def get_favicon():
    raise HTTPException(status_code=404)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8000/entries/") as response:
            body = await response.json()
            entry_list: List[Entry] = []
            for item in body.get("items"):
                entry_list.append(Entry(id=None, **item))

            return templates.TemplateResponse(
                "index.jinja",
                {
                    "request": request,
                    "entries": entry_list,
                },
            )


@app.get("/{entry_id}", response_class=HTMLResponse)
async def index(request: Request, entry_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://127.0.0.1:8000/entries/{entry_id}") as response:
            if response.status != 200:
                return templates.TemplateResponse(
                    "error.jinja",
                    {
                        "request": request,
                        "status_code": response.status,
                        "reason": response.reason,
                    },
                )

            body = await response.json()
            body["entry"]["id"] = None
            detailed_entry = DetailedEntry(**body)
            detailed_dict = detailed_entry.dict()
            del detailed_dict["rekor_entry"]["spec"]["publicKey"]
            rekor_entry = dumps(detailed_dict.get("rekor_entry"), indent=4)

            return templates.TemplateResponse(
                "details.jinja",
                {
                    "request": request,
                    "entry": detailed_entry,
                    "rekor_entry": rekor_entry,
                },
            )
