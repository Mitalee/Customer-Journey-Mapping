# Map JSON format

The render script reads one JSON file:

```json
{
  "title": "IRCTC: booking a regular train ticket",
  "persona": "Working professional booking on a laptop",
  "jtbd": "Get confirmed seats for a family trip next month",
  "trigger": "Family decides on the trip dates",
  "scenario": "Regular (non-Tatkal) booking, happy path",
  "success": "Confirmed seats in a class the family can live with, at a known price",
  "steps": [
    {"label": "Opens site", "score": 0.5},
    {"label": "Login, CAPTCHA", "score": -1.5, "fix": "Google login", "fix_score": 0.8},
    {"label": "Sees trains", "score": 1.5, "why": "Trains load fast"},
    {"label": "No seats", "score": -1.8, "fix": "Other trains", "fix_score": 1},
    {"label": "Ticket booked", "score": 1.9, "why": "Seat confirmed"}
  ]
}
```

Fields per step:

| Field | Required | Meaning |
|---|---|---|
| `label` | yes | The step, as a short phrase (under about 28 characters, since it's drawn vertically under the axis). |
| `score` | yes | Feeling from -2 (crying) to +2 (ecstatic). Halves and decimals are fine. |
| `why` | no | Short reason for a delight (peaks only, under about 22 characters). Drawn above the point. |
| `fix` | no | Short name of the feature that lifts a dip (under about 18 characters). Drawn just above the green line. |
| `fix_score` | no | Where the curve would sit with the fix in place. Defaults to the original score if no fix. |

The green "with fixes" line uses `fix_score` where a fix exists and `score` everywhere else.

Top-level fields, all drawn above the map so the picture explains itself without the chat:

| Field | Meaning |
|---|---|
| `title` | One line naming the product and the journey. |
| `persona` | The one specific person this map is about. |
| `jtbd` | What the person is really trying to get done, in their words. |
| `trigger` | The event that starts the journey. |
| `scenario` | Which path is drawn (happy path, a named edge case, peak load). |
| `success` | What "done well" looks like from the person's side. Make it something you could check. |

All of them are optional for the script, but always fill in `persona`, `jtbd` and `success`: without them, readers can't tell whose pain they're looking at or what "good" means.
