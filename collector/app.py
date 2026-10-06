"""
Feedback collector for the customer-journey-map skill.

Receives two kinds of events from PMs' laptops (sent by send_feedback.py):
  - map_drawn: the question, scope and map, sent as soon as the map is shown
  - feedback:  the thumbs up/down and "what was missing", sent later

Both events share a run_id, so they end up as one row per run.

Pages:
  POST /events               where send_feedback.py sends events
  GET  /review               the review page, thumbs-down first
  GET  /runs/{run_id}/map    the map for one run, drawn as SVG
  GET  /health               quick check that the server is up

Storage is a single SQLite file. No LLM key is needed here: the PMs'
own Copilot does the thinking; this server only listens and stores.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from html import escape

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

# Reuse the skill's own render script for the map page, so the review page
# shows exactly the picture the PM saw.
SKILL_SCRIPTS = os.environ.get("CJM_SKILL_SCRIPTS", "/app/customer-journey-map/scripts")
sys.path.append(SKILL_SCRIPTS)
import render_map  # noqa: E402  (import after the path is set on purpose)

# The database lives on a mounted volume (see docker-compose.yml), so the
# data survives container restarts and rebuilds.
DB_PATH = os.environ.get("CJM_DB_PATH", "/data/cjm.db")

app = FastAPI(title="CJM feedback collector")


def open_db():
    """Open the database, creating the table the first time."""
    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id         TEXT PRIMARY KEY,
            user           TEXT,
            skill_version  TEXT,
            question       TEXT,
            persona        TEXT,
            jtbd           TEXT,
            success        TEXT,
            journey_json   TEXT,
            answer_text    TEXT,
            drawn_at       TEXT,
            rating         TEXT,
            missing        TEXT,
            followup_count INTEGER,
            rated_at       TEXT
        )
        """
    )
    return connection


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events")
async def receive_event(request: Request):
    event = await request.json()

    event_type = event.get("event_type")
    run_id = event.get("run_id")
    if event_type not in ("map_drawn", "feedback") or not run_id:
        raise HTTPException(status_code=400, detail="Need event_type (map_drawn or feedback) and run_id.")

    received_at = datetime.now(timezone.utc).isoformat()
    connection = open_db()

    # Make sure a row exists for this run. A feedback event can arrive first
    # if the map_drawn event was stuck in a laptop's outbox, so either event
    # type may be the one that creates the row.
    connection.execute(
        "INSERT OR IGNORE INTO runs (run_id, user, skill_version) VALUES (?, ?, ?)",
        (run_id, event.get("user", ""), event.get("skill_version", "")),
    )

    if event_type == "map_drawn":
        journey = event.get("journey", {})
        connection.execute(
            """
            UPDATE runs
            SET question = ?, persona = ?, jtbd = ?, success = ?,
                journey_json = ?, answer_text = ?, drawn_at = ?
            WHERE run_id = ?
            """,
            (
                event.get("question", ""),
                journey.get("persona", ""),
                journey.get("jtbd", ""),
                journey.get("success", ""),
                json.dumps(journey),
                event.get("answer_text", ""),
                event.get("sent_at", received_at),
                run_id,
            ),
        )
    else:
        connection.execute(
            """
            UPDATE runs
            SET rating = ?, missing = ?, followup_count = ?, rated_at = ?
            WHERE run_id = ?
            """,
            (
                event.get("rating", ""),
                event.get("missing", ""),
                event.get("followup_count", 0),
                event.get("sent_at", received_at),
                run_id,
            ),
        )

    connection.commit()
    connection.close()
    return {"status": "stored", "run_id": run_id}


@app.get("/runs/{run_id}/map")
def show_map(run_id: str):
    connection = open_db()
    row = connection.execute("SELECT journey_json FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    connection.close()

    if row is None or not row["journey_json"]:
        raise HTTPException(status_code=404, detail="No map stored for this run yet.")

    journey = json.loads(row["journey_json"])
    try:
        svg_text = render_map.render(journey)
    except Exception as error:
        # A malformed journey shouldn't crash the review page; show why instead.
        raise HTTPException(status_code=422, detail=f"Could not draw this map: {error}")
    return Response(content=svg_text, media_type="image/svg+xml")


@app.get("/review", response_class=HTMLResponse)
def review():
    connection = open_db()
    # Thumbs-down first (most to learn from), then unrated, then thumbs-up.
    rows = connection.execute(
        """
        SELECT * FROM runs
        ORDER BY
            CASE rating WHEN 'down' THEN 0 WHEN 'up' THEN 2 ELSE 1 END,
            drawn_at DESC
        """
    ).fetchall()
    connection.close()

    total = len(rows)
    thumbs_up = 0
    thumbs_down = 0
    for row in rows:
        if row["rating"] == "up":
            thumbs_up = thumbs_up + 1
        elif row["rating"] == "down":
            thumbs_down = thumbs_down + 1
    unrated = total - thumbs_up - thumbs_down

    table_rows = []
    for row in rows:
        rating = row["rating"] or "not rated"
        map_link = ""
        if row["journey_json"]:
            map_link = f'<a href="/runs/{escape(row["run_id"])}/map" target="_blank">map</a>'
        table_rows.append(
            "<tr>"
            f"<td>{escape(row['drawn_at'] or '')[:16]}</td>"
            f"<td>{escape(row['user'] or '')}</td>"
            f"<td>{escape(row['question'] or '')}</td>"
            f"<td>{escape(row['persona'] or '')}</td>"
            f"<td>{escape(row['jtbd'] or '')}</td>"
            f"<td class='{escape(rating.replace(' ', '-'))}'>{escape(rating)}</td>"
            f"<td>{escape(row['missing'] or '')}</td>"
            f"<td>{row['followup_count'] if row['followup_count'] is not None else ''}</td>"
            f"<td>{escape(row['skill_version'] or '')}</td>"
            f"<td>{map_link}</td>"
            "</tr>"
        )

    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>CJM skill feedback</title>
<style>
  body {{ font-family: Helvetica, Arial, sans-serif; margin: 24px; color: #2C2C2A; }}
  .stats span {{ display: inline-block; margin-right: 24px; font-size: 18px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 16px; font-size: 13px; }}
  th, td {{ border-bottom: 1px solid #D3D1C7; padding: 8px; text-align: left; vertical-align: top; }}
  .down {{ color: #A32D2D; font-weight: bold; }}
  .up {{ color: #3B6D11; font-weight: bold; }}
  .not-rated {{ color: #888780; }}
</style></head><body>
<h1>Customer journey map skill: feedback</h1>
<div class="stats">
  <span>Runs: {total}</span><span>Thumbs up: {thumbs_up}</span>
  <span>Thumbs down: {thumbs_down}</span><span>Not rated: {unrated}</span>
</div>
<table>
<tr><th>When</th><th>User</th><th>Question</th><th>Persona</th><th>Job to be done</th>
<th>Rating</th><th>What was missing</th><th>Follow-ups</th><th>Version</th><th></th></tr>
{''.join(table_rows)}
</table></body></html>"""
    return HTMLResponse(page)
