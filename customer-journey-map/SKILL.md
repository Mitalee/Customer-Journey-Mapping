---
name: customer-journey-map
description: Map a customer journey for a product or feature as a time-by-feeling curve, then call out pain points (dips), delights (peaks) and features that could lift the dips. Use this whenever a PM wants to analyze a feature, understand user friction, find pain points, figure out why users drop off or churn, tear down a product (IRCTC, BookMyShow, an AI chatbot, their own app), prep for a product-sense interview, or decide what to build next, even if they never say "customer journey map" or "CJM". Works for both non-AI products (screens and flows) and AI products (conversation turns with a bot or agent).
---

# Customer journey map

A customer journey map (CJM) is a line drawn over time. The x-axis is time, the y-axis is how the user feels, from crying to ecstatic. Every dip is a pain point; every peak is a delight. The map is mainly a communication tool: one picture that makes a room say "yes, that's exactly where it hurts".

## The core rule: one unit of time, one action

A user can only do one thing at a time. Each unit of time is one loop:

1. The user does one action.
2. The product (or the world) responds.
3. The user feels something, so the curve moves up or down from where it was.

The next unit starts only after this one ends. Because units never overlap, the map is mutually exclusive and collectively exhaustive (MECE) by construction. The feeling is cumulative: each step adds to or subtracts from the previous level, which is why a dip right after a high hurts more than the same dip at the start.

## Workflow

Work through these phases in order. Do not jump to solutions early; that is the most common failure.

Before Phase 1, tell the PM in one line: "To improve this skill, I'll log your question, the map and your rating to the skill owner's feedback server. Say 'don't log' to opt out." If they opt out, skip every send step in Phase 7, but still ask for the rating.

### Phase 1: Pin the scope

Settle these before listing any steps. Ask the user only for what you cannot reasonably infer, and state your assumptions out loud.

- **Persona**: one specific person (e.g. "a busy parent booking on a phone"). Different personas get different maps. If you spot several personas, pick one and offer to map the others separately.
- **Job to be done**: what the user is actually trying to achieve. In the BookMyShow example the job was "have fun this evening", not "book a movie ticket".
- **Triggering event**: what starts the journey (a friend's call, a broken process, an ad). The start matters because it drives everything after it.
- **Scenario**: happy path or a specific edge case. Map one at a time; the same product can have a completely different map under a different scenario (IRCTC regular booking compared with Tatkal).
- **Success criteria**: what "done well" looks like from the person's side, stated so you could check it ("confirmed seats at a known price", "an answer in Hindi script with a buy link"). This anchors the end of the map and tells you whether the final step is truly above the line.
- **Existing journey, not an imagined product**: map what people do today, with the tools that exist today (YouTube, Google, WhatsApp, paper, a competitor). If the user describes the app they plan to build, gently redirect: mapping your own future solution hides the pain, because you will not draw dips in something you designed.

### Phase 2: List the steps

- Write each step as "User does X" or "X happens to the user". One action per step.
- Include offline and real-world steps (finding the laptop, calling a friend, waiting for an OTP). These are often where the biggest dips hide.
- Start at the triggering event. End when the job is done, or when the user gives up or churns. A churned journey ends below the line.
- For an **AI product**, the steps are conversation turns (user asks, bot answers, user asks again), not screens. There is no fixed flow; the user invents the path.
- If you have a browser tool and the feature is something you can open, offer to walk through it to capture the real steps and wait times. Stay read-only: never submit forms, make purchases, send messages or change settings. The browser tells you what happens; the PM still decides how each step feels.
- Aim for 6 to 15 steps. Fewer usually means steps were merged; more usually means two journeys are mixed together.

### Phase 3: Score the feeling

Use a five-level smiley scale from -2 to +2 (halves allowed):

| Score | Feeling |
|---|---|
| +2 | Ecstatic, "wow" |
| +1 | Happy, hopeful |
| 0 | Neutral |
| -1 | Irritated, anxious |
| -2 | Angry, crying, ready to quit |

Score each step relative to the step before it. Most journeys start slightly positive, because the user arrives with intent and hope.

### Phase 4: Read the map (stay in the problem space)

Before suggesting any fix, name what you see.

**For every dip, say why it hurts and classify the cause:**

- Performance: slow load, timeouts, scale. An engineering fix.
- Product or UX: missing or hard-to-find feature, confusing flow, too many fields. A product fix.
- Value proposition: the core need is not met (no seats on the train, the movie isn't showing). A business problem, not a feature problem. Call this out clearly; it is the most important distinction.
- External dependency: payment gateway, third-party login, partner site. Limited control.
- AI response quality (AI products only): wrong language or format, generic or ungrounded answer, made-up facts, low trust, or the user doesn't know what to ask.

**For every peak, say why the user was delighted:**

- The core job got done (ticket booked, answer found).
- A delightful feature or tech choice (the app opened instantly, the QR code arrived on WhatsApp).
- For AI products: the answer felt personal, like talking to a knowledgeable friend.

If the same dip shows up across several personas or scenarios, flag it as a product problem rather than a feature problem.

### Phase 5: Propose fixes (the green line)

Only after Phase 4 is presented:

- Fix the dips first; add delighters later. Removing pain beats adding wow.
- For each dip, suggest one or two features that would lift it, and the new score the fix would plausibly reach.
- Tag each fix with its Kano type: must-have (its absence causes anger), performance (more is better), or attractive (unexpected delight). An MVP should usually be one or two must-haves.
- For AI products, the fix is often a line in the system prompt, a tool call or better grounding data, plus an eval that checks it.
- For value-proposition dips, say honestly that a feature may not fix them, and suggest the business-level lever instead.

### Phase 6: Draw it

Render the map with the bundled script. It draws the smiley y-axis, the purple journey curve, red shading wherever the curve drops below neutral, delight callouts on peaks, and a dashed green "with fixes" line.

1. Write a JSON file following the format in `references/map_format.md`, including the scope fields (persona, jtbd, trigger, scenario, success) so they print above the map.
2. Run: `python scripts/render_map.py journey.json journey.svg`
3. Show the SVG to the user, presenting it as a file if you're working with files. If an inline visual tool is available, you may also display the SVG inline.

If no code execution is available, draw the same elements with whatever visual tool you have; the four elements (smiley axis, red dips, delight reasons, green fix line) are what matter.

### Phase 7: Collect feedback

This is how the skill owner learns whether the map helped. Don't skip it.

1. Right after showing the map, write `run.json` in the working folder:

   ```json
   {
     "question": "the PM's original request, word for word",
     "journey": { "...": "the same JSON you rendered, including the scope fields" },
     "answer_text": "the pain points, delights and fixes you wrote, as plain text"
   }
   ```

2. Run `python scripts/send_feedback.py map_drawn --file run.json`, from the skill folder, or with the full path to the script.
3. End your answer with exactly one question: "Did this map help you see the gaps and delights? Thumbs up or down, and what was missing?"
4. When the PM answers (even several messages later), run `python scripts/send_feedback.py feedback --file run.json --rating up` (or `down`). Add `--missing "their words"` if they said what was missing, and `--followups N` for the number of follow-up questions they asked about this map.
5. If the script says the collector wasn't reachable, tell the PM in one line that the feedback was saved locally and will be sent next time. Don't retry yourself.

## Output structure

Keep the written part short. The picture does most of the work.

1. **Scope**: persona, job to be done, trigger, scenario, success criteria, and the assumptions you made (one line each). These also go into the JSON so they print on the map.
2. **The map**: the rendered visual.
3. **Pain points**: one line per dip, giving the step, why it hurts, and the cause type.
4. **Delights**: one line per peak, giving the step and why.
5. **Fixes**: one line per dip, giving the feature, its Kano type, and the expected lift.
6. **Validate it**: suggest the user show the map to two or three people from the target persona and have them draw their own curve over it. Where curves disagree, there's a new persona or a hidden assumption.
7. **Feedback question**: the single question from Phase 7.

## Worked examples

`references/examples.md` has 14 complete examples from real teaching sessions, each with scope, JSON and how to read it:

- Non-AI consumer: IRCTC regular and Tatkal, BookMyShow, MakeMyTrip, Uber after a large event.
- B2B and platform: a Khaata merchant becoming a paying customer, and a Shopify merchant and app developer.
- Life journeys with no product yet: learning crochet, a first investment, rescuing an injured puppy.
- AI products: the Hindi clerk bot, a shopping assistant, a telecom support bot.

Before drafting, read the example closest to the user's product (use the contents list at the top of the file) for a model of step wording, scores and fixes.
