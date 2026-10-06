# Customer journey map skill

A Claude skill that helps a PM map a customer journey as a time-by-feeling curve, then call out pain points (dips), delights (peaks) and features that could lift the dips.

Each map prints its scope (persona, job to be done, trigger, scenario, success criteria) and draws:

- a smiley-face y-axis, from crying to ecstatic
- red shading wherever the journey drops below neutral
- callouts explaining why the user was delighted at each peak
- a dashed green line showing the journey with fixes in place

The core rule: a user can only do one thing at a time. Each unit of time is one loop (the user acts, the product responds, the user feels), so the map is mutually exclusive and collectively exhaustive by construction.

## What's in this repo

| Path | What it is |
|---|---|
| `customer-journey-map.skill` | The packaged skill, ready to install in Claude |
| `customer-journey-map/SKILL.md` | The workflow Claude follows |
| `customer-journey-map/references/examples.md` | 14 worked examples (IRCTC, BookMyShow, MakeMyTrip, Uber, Shopify, AI chatbots and more) |
| `customer-journey-map/references/map_format.md` | The JSON format the render script reads |
| `customer-journey-map/scripts/render_map.py` | Turns a journey JSON into an SVG map |
| `rendered-examples/` | Every worked example as JSON, SVG and PNG |

## Use it in Claude

Install `customer-journey-map.skill` as a skill in Claude, then ask something like "analyze the checkout flow of our app" or "where are users dropping off in onboarding?".

## Render a map yourself

Needs Python 3, no extra packages:

```bash
python customer-journey-map/scripts/render_map.py rendered-examples/01-irctc.json my-map.svg
```

Open the SVG in any browser.
