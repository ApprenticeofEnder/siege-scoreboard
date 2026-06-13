import asyncio
import random
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
TEAMS = ["Alpha", "Bravo", "Charlie", "Delta"]


def format_sse_data(payload: str) -> str:
    """Encode HTML (or any payload) as valid multi-line SSE data fields."""
    return "".join(f"data: {line}\n" for line in payload.splitlines()) + "\n"

app = FastAPI(title="Siege Scoreboard")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=ROOT_DIR / "templates")


def theme_from_request(request: Request) -> str:
    theme = request.cookies.get("theme", "system")
    if theme in {"system", "light", "dark"}:
        return theme
    return "system"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/demo", status_code=302)


@app.get("/demo")
def demo(request: Request):
    return templates.TemplateResponse(
        request,
        "demo.html",
        {
            "theme": theme_from_request(request),
            "title": "Live Events",
        },
    )


async def event_stream(request: Request):
    tick = 0
    while True:
        if await request.is_disconnected():
            break

        tick += 1
        team = random.choice(TEAMS)
        delta = random.choice([50, 25, -25, -10, 10, -50])
        timestamp = datetime.now(UTC).strftime("%H:%M:%S")

        row_html = templates.env.get_template("partials/event_row.html").render(
            tick=tick,
            team=team,
            delta=delta,
            timestamp=timestamp,
        )
        yield format_sse_data(row_html.strip())
        await asyncio.sleep(2)


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    return StreamingResponse(
        event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
