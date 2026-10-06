"""
Send one customer-journey-map run to the feedback collector.

The agent calls this twice per run:

  1. Right after the map is shown:
       python scripts/send_feedback.py map_drawn --file run.json
     This creates a run_id, writes it back into run.json, and sends the
     question, scope and map. Sending this early means the collector can
     count runs that never got rated (agents sometimes skip the last step).

  2. When the PM answers the feedback question:
       python scripts/send_feedback.py feedback --file run.json --rating up --missing "..." --followups 2
     This sends the rating for the same run_id.

Where it sends: the collector_url in config.json, unless the
CJM_COLLECTOR_URL environment variable is set (handy for testing a new
server without editing the repo).

If the collector can't be reached, the event is saved to an outbox file
in the user's home folder and retried on the next call, so a sleeping
server never loses feedback.

Only the Python standard library is used, so PMs never have to install anything.
"""

import argparse
import getpass
import json
import os
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timezone


# Paths are worked out from this file's location, so the script works no
# matter which folder the agent runs it from.
SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
SKILL_FOLDER = os.path.dirname(SCRIPT_FOLDER)
CONFIG_PATH = os.path.join(SKILL_FOLDER, "config.json")

# One outbox per user, outside the repo, so pending events survive a skill update.
OUTBOX_PATH = os.path.join(os.path.expanduser("~"), ".cjm_outbox.jsonl")

# Short timeout: if the server is down we want to fall back to the outbox
# quickly instead of making the PM wait.
TIMEOUT_SECONDS = 5


def load_config():
    """Read config.json and apply the environment-variable override for the URL."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    override_url = os.environ.get("CJM_COLLECTOR_URL", "")
    if override_url:
        config["collector_url"] = override_url

    return config


def find_user():
    """
    Identify who ran the skill.

    The git email is preferred because every PM using Copilot CLI has git set
    up, and an email is easier to recognise in the review page than a
    laptop login name. Falls back to the operating-system username.
    """
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        email = result.stdout.strip()
        if email:
            return email
    except Exception:
        # git missing or slow: not worth failing the whole send over
        pass
    return getpass.getuser()


def post_event(collector_url, event):
    """Send one event. Returns True on success, False if the server couldn't be reached."""
    url = collector_url.rstrip("/") + "/events"
    body = json.dumps(event).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def save_to_outbox(event):
    """Append an event that couldn't be sent, one JSON object per line."""
    with open(OUTBOX_PATH, "a", encoding="utf-8") as outbox:
        outbox.write(json.dumps(event) + "\n")


def flush_outbox(collector_url):
    """
    Try to send everything waiting in the outbox.

    Events that still fail are written back, so nothing is dropped.
    """
    if not os.path.exists(OUTBOX_PATH):
        return

    with open(OUTBOX_PATH, "r", encoding="utf-8") as outbox:
        lines = outbox.readlines()

    still_pending = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        event = json.loads(line)
        sent = post_event(collector_url, event)
        if not sent:
            still_pending.append(line)

    if len(still_pending) == 0:
        os.remove(OUTBOX_PATH)
    else:
        with open(OUTBOX_PATH, "w", encoding="utf-8") as outbox:
            for line in still_pending:
                outbox.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description="Send a CJM run or rating to the collector.")
    parser.add_argument("event_type", choices=["map_drawn", "feedback"])
    parser.add_argument("--file", required=True, help="Path to run.json")
    parser.add_argument("--rating", choices=["up", "down"], help="Feedback only")
    parser.add_argument("--missing", default="", help="Feedback only: what the PM said was missing")
    parser.add_argument("--followups", type=int, default=0, help="Feedback only: follow-up questions asked")
    args = parser.parse_args()

    config = load_config()
    collector_url = config["collector_url"]

    with open(args.file, "r", encoding="utf-8") as run_file:
        run = json.load(run_file)

    # The first event creates the run_id; the feedback event reuses it so the
    # collector can join the rating to the right map.
    if args.event_type == "map_drawn":
        run["run_id"] = str(uuid.uuid4())
        with open(args.file, "w", encoding="utf-8") as run_file:
            json.dump(run, run_file, indent=2)
    elif "run_id" not in run:
        print("run.json has no run_id. Send map_drawn first.")
        sys.exit(1)

    event = {
        "event_type": args.event_type,
        "run_id": run["run_id"],
        "user": find_user(),
        "skill_version": config.get("skill_version", "unknown"),
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.event_type == "map_drawn":
        event["question"] = run.get("question", "")
        event["journey"] = run.get("journey", {})
        event["answer_text"] = run.get("answer_text", "")
    else:
        if not args.rating:
            print("Feedback needs --rating up or --rating down.")
            sys.exit(1)
        event["rating"] = args.rating
        event["missing"] = args.missing
        event["followup_count"] = args.followups

    # Older events go first, so the collector receives them in order.
    flush_outbox(collector_url)

    sent = post_event(collector_url, event)
    if sent:
        print(f"Sent {args.event_type} for run {run['run_id']}.")
    else:
        save_to_outbox(event)
        print(f"Collector not reachable. Saved {args.event_type} locally; it will be sent next time.")


if __name__ == "__main__":
    main()
