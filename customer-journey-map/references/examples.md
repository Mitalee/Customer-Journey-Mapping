# Worked examples

Every example below comes from a real teaching session. Each has its scope (persona, job to be done, trigger, scenario, success), the JSON the render script reads, and a short "how to read it". Read the one closest to the user's product before drafting a new map.

## Contents

Non-AI consumer products
1. IRCTC: regular ticket booking
2. IRCTC: Tatkal booking (same product, different scenario)
3. BookMyShow: a spontaneous evening out
4. MakeMyTrip: booking a hotel in Goa
5. Uber: getting home after a large event

B2B and platform products
6. Khaata: a Shopify merchant becoming a paying customer
7. Shopify App Store: a merchant adding an app
8. Shopify App Store: an app developer's journey

Life journeys (map these before building anything)
9. Learning crochet with today's tools
10. Making a first investment
11. Rescuing an injured puppy

AI products
12. Hindi clerk chatbot
13. Santra.com shopping assistant
14. Telecom support chatbot

---

## 1. IRCTC: regular ticket booking

```json
{
  "title": "IRCTC: booking a regular train ticket",
  "persona": "Working professional booking on a laptop",
  "jtbd": "Get confirmed seats for a family trip next month",
  "trigger": "Family decides on the trip dates",
  "scenario": "Regular (non-Tatkal) booking, happy path",
  "success": "Confirmed seats in a class the family can live with, at a known price",
  "steps": [
    {"label": "Family plans a trip", "score": 0.5},
    {"label": "Opens IRCTC site", "score": 0.3},
    {"label": "Login, CAPTCHA, OTP", "score": -1.5, "fix": "Google login", "fix_score": 0.6},
    {"label": "Finally logs in", "score": 0.2},
    {"label": "Searches route, sees trains", "score": 1.4, "why": "Trains load fast"},
    {"label": "No seats in AC classes", "score": -1.6, "fix": "Suggest other trains", "fix_score": 0.8},
    {"label": "Finds 2 sleeper seats", "score": 0.9},
    {"label": "Sees dynamic price", "score": -0.6},
    {"label": "Fills passenger details", "score": -0.3},
    {"label": "Payment page loading", "score": -1.2, "fix": "Show live status", "fix_score": 0.4},
    {"label": "Ticket booked", "score": 1.8, "why": "Seat confirmed"}
  ]
}
```

How to read it:
- Login dip: product/UX. Security friction built for fraudsters, paid for by regular users.
- No seats: value proposition. A feature softens it; it can't create seats.
- Payment wait: external dependency (payment gateway). You can't control the gateway, but you can tell the user what's happening.
- Even with three dips, this user would rate the trip "4 stars". The map shows what the rating hides.

## 2. IRCTC: Tatkal booking

```json
{
  "title": "IRCTC: Tatkal booking at 10 am",
  "persona": "Same professional, now needing to travel tomorrow",
  "jtbd": "Get any confirmed seat for an urgent trip",
  "trigger": "Unexpected travel tomorrow; Tatkal window opens",
  "scenario": "Tatkal rush, peak load",
  "success": "Any confirmed seat within the first few minutes",
  "steps": [
    {"label": "Waits for 10 am window", "score": 0.5},
    {"label": "Login, CAPTCHA", "score": -1.0, "fix": "Log in early", "fix_score": 0.3},
    {"label": "Search loads forever", "score": -1.8, "fix": "Virtual queue", "fix_score": -0.2},
    {"label": "Trains show, seats gone", "score": -2.0},
    {"label": "Retries another class", "score": -1.5},
    {"label": "Payment page fails", "score": -2.0, "fix": "Hold seat in queue", "fix_score": -0.5},
    {"label": "Gives up", "score": -2.0}
  ]
}
```

How to read it:
- Same product, different scenario, completely different map. That's why you map one scenario at a time.
- Almost everything here is performance at extreme scale, plus a value-prop dip (seats gone). Features only soften it, which is why the green line stays near neutral.

## 3. BookMyShow: a spontaneous evening out

```json
{
  "title": "BookMyShow: a spontaneous evening out",
  "persona": "Young professional, app already installed and logged in",
  "jtbd": "Have fun with a friend this evening (not 'book a movie')",
  "trigger": "Friend calls at 4 pm and suggests the mall and a movie",
  "scenario": "Browses by nearest cinema",
  "success": "Out with the friend tonight, tickets on the phone, no surprise costs",
  "steps": [
    {"label": "Sitting idle at 4 pm", "score": 0},
    {"label": "Friend suggests a movie", "score": 1.0},
    {"label": "Opens BookMyShow", "score": 1.5, "why": "Opens instantly"},
    {"label": "Ads and pop-ups", "score": -0.8, "fix": "Fewer pop-ups", "fix_score": 0.8},
    {"label": "Browses nearest cinema", "score": 0.5},
    {"label": "No movie of interest", "score": -1.5, "fix": "Nearby alternatives", "fix_score": 0.3},
    {"label": "Finds favourite comedian", "score": 1.8, "why": "Found my comedian"},
    {"label": "Price looks fine", "score": 1.2},
    {"label": "Books 2 tickets", "score": 1.3},
    {"label": "Sees about 10% fee", "score": -0.8, "fix": "Show fee upfront", "fix_score": 0.8},
    {"label": "Pays by UPI", "score": 0.3},
    {"label": "QR code on WhatsApp", "score": 1.6, "why": "Nothing to carry"}
  ]
}
```

How to read it:
- The job was "have fun", which is why the comedian rescue counts as success, not failure.
- Pop-ups: product (a business-driven choice that costs experience). No movie: value prop. The fee: pricing and trust.
- Fix the dips before adding delighters. Most of this map is already above the line, which means it's a mature product.

## 4. MakeMyTrip: booking a hotel in Goa

```json
{
  "title": "MakeMyTrip: booking a hotel in Goa",
  "persona": "Busy parent booking on a phone, app installed",
  "jtbd": "Lock in a good-value, well-reviewed hotel for a family trip",
  "trigger": "Family trip dates agreed on WhatsApp",
  "scenario": "Search by city, filter by rating",
  "success": "Booked a hotel the family trusts, within budget, with confirmation in hand",
  "steps": [
    {"label": "Decides to book a hotel", "score": 1.0},
    {"label": "Opens the app", "score": 0.8},
    {"label": "App slow to load", "score": -0.5, "fix": "Faster start", "fix_score": 0.6},
    {"label": "Goes to Hotels tab", "score": 0.6},
    {"label": "Types Goa", "score": 0.7},
    {"label": "Results listed", "score": 1.0},
    {"label": "Scrolls a cluttered list", "score": -1.0, "fix": "Sort by fit", "fix_score": 0.6},
    {"label": "Filters by rating", "score": 0.5},
    {"label": "Opens top hotel reviews", "score": 0.2},
    {"label": "Dislikes it, goes back", "score": -1.2},
    {"label": "Second hotel looks good", "score": 1.0},
    {"label": "Price and package fit", "score": 1.5, "why": "Fits my budget"},
    {"label": "Long booking form", "score": -0.8, "fix": "Autofill details", "fix_score": 0.8},
    {"label": "Pays, processing", "score": -0.4},
    {"label": "Booking confirmed", "score": 1.9, "why": "Job done"}
  ]
}
```

How to read it:
- Performance (slow start), UX (cluttered list, long form) and value prop (the first hotel itself) are all on one map. Naming which is which builds credibility.
- "Dislikes it, goes back" is about the hotel, not the app, so no feature fix is drawn.
- Every persona choice (phone or laptop, city or hotel name) creates a different map. Pick one.

## 5. Uber: getting home after a large event

```json
{
  "title": "Uber: getting home after a concert",
  "persona": "Concert-goer leaving with thousands of others",
  "jtbd": "Get home quickly and safely after the event",
  "trigger": "The show ends and everyone exits at once",
  "scenario": "Peak demand at a large venue",
  "success": "In a car within a few minutes, at a price agreed upfront",
  "steps": [
    {"label": "Exits the venue", "score": 0.5},
    {"label": "Opens Uber", "score": 0.5},
    {"label": "Checks availability", "score": 0},
    {"label": "Books a ride", "score": 0.8},
    {"label": "Waits", "score": -0.6},
    {"label": "Waits longer", "score": -1.3},
    {"label": "Gives up, cancels", "score": -2.0, "fix": "Event pickup zone", "fix_score": 0.2},
    {"label": "Walks away from venue", "score": -1.2},
    {"label": "Books again", "score": -0.3},
    {"label": "Sees surge price", "score": -1.5, "fix": "Lock price at book", "fix_score": -0.2},
    {"label": "Accepts surge", "score": -0.8},
    {"label": "Hunts for pickup spot", "score": -1.0, "fix": "Clear pickup pins", "fix_score": 0.3},
    {"label": "Finds the car", "score": 1.0},
    {"label": "Reaches home", "score": 1.5, "why": "Finally home"}
  ]
}
```

How to read it:
- Most of this journey is below the line, and the pains compound: waiting leads to cancelling, which leads to walking, which leads to surge.
- The root dips are waiting, communication, pickup confusion and surge. Name these before solutioning.
- Built on a napkin before AI tools existed, this map was enough to drive an interview discussion.

## 6. Khaata: a Shopify merchant becoming a paying customer

```json
{
  "title": "Khaata: from sign-up to first recharge",
  "persona": "Accountant at a small Shopify store selling bike parts",
  "jtbd": "Get Shopify orders into Tally without manual entry",
  "trigger": "Signs up on the website while looking for an accounting tool",
  "scenario": "Sales-led: call, demo, follow-ups, self-serve recharge",
  "success": "Invoices flowing into Tally at a per-invoice price the owner approves",
  "steps": [
    {"label": "Signs up on website", "score": 0.5},
    {"label": "Gets a sales call", "score": 0},
    {"label": "Still hunting a free app", "score": -0.5, "fix": "Show free points", "fix_score": 0.5},
    {"label": "Installs app, books demo", "score": 0.8},
    {"label": "Same-day demo", "score": 1.5, "why": "Fast, personal demo"},
    {"label": "Feels it's too expensive", "score": -1.2, "fix": "Rate calculator", "fix_score": 0.2},
    {"label": "Needs internal approval", "score": -0.8},
    {"label": "16 days of follow-ups", "score": -0.5},
    {"label": "Decides before CA objects", "score": 0.5},
    {"label": "Sees self-serve recharge", "score": 1.2, "why": "Clear per-invoice rate"},
    {"label": "Recharges", "score": 1.5},
    {"label": "Waits for setup help", "score": -0.6, "fix": "Guided onboarding", "fix_score": 0.8}
  ]
}
```

How to read it:
- Map one real customer at a time. Do this for 20 to 30 customers and the repeated dips become the product roadmap and the sales playbook.
- Write only what you're convinced of. An early version of this map listed ads, referrals and trainings the business doesn't actually do; those lines were filler copied from an AI tool.
- The last dip (waiting for setup) points at onboarding, which is still done only through live demos.

## 7. Shopify App Store: a merchant adding an app

```json
{
  "title": "Shopify: a merchant adding a third-party app",
  "persona": "Growing Shopify merchant",
  "jtbd": "Plug a gap in the selling lifecycle without hurting the store",
  "trigger": "Hits obstacles the core product doesn't solve",
  "scenario": "Finds, trials and later uninstalls an app",
  "success": "An app that adds revenue, with data handled safely",
  "steps": [
    {"label": "Looks for a sales channel", "score": 0.5},
    {"label": "Registers a store", "score": 1.2},
    {"label": "Revenue grows", "score": 2.0, "why": "Core product works"},
    {"label": "Hits selling obstacles", "score": -0.8},
    {"label": "Searches web for apps", "score": -0.3},
    {"label": "Searches App Store", "score": -0.3, "fix": "Problem-based search", "fix_score": 0.6},
    {"label": "Checks ratings", "score": 0.8},
    {"label": "Starts a trial", "score": 0.8},
    {"label": "Authorizes the app", "score": 1.0},
    {"label": "Sees value added", "score": 1.3},
    {"label": "Upgrades the app", "score": 1.8, "why": "Worth paying for"},
    {"label": "App degrades results", "score": -1.0, "fix": "Impact alerts", "fix_score": 0.6},
    {"label": "Uninstalls", "score": -1.5},
    {"label": "Worries about data", "score": -1.8, "fix": "Deletion receipt", "fix_score": -0.2}
  ]
}
```

How to read it:
- The original sketch kept "hits selling obstacles" above the line. It's the trigger pain, so it belongs below.
- The deepest dip is churn plus the data worry. That same moment is the developer's deepest dip (example 8), which is the strongest insight across the two maps.

## 8. Shopify App Store: an app developer's journey

```json
{
  "title": "Shopify: an app developer's journey",
  "persona": "Indie app developer",
  "jtbd": "Build a profitable app on the Shopify ecosystem",
  "trigger": "Spots a gap in what Shopify merchants can do",
  "scenario": "Builds, gets listed, gains then loses a merchant",
  "success": "Listed app with merchants who keep paying",
  "steps": [
    {"label": "Researches product gaps", "score": 0.5},
    {"label": "Checks profitability", "score": 1.2},
    {"label": "Tests auth in sandbox", "score": -1.0, "fix": "Better sandbox", "fix_score": 0.4},
    {"label": "Adds integration points", "score": 0.3},
    {"label": "Builds an MVP", "score": 0.8},
    {"label": "Submits the app", "score": 1.2},
    {"label": "Eligibility review", "score": -1.5, "fix": "Review checklist", "fix_score": 0.3},
    {"label": "Revenue path attached", "score": 0},
    {"label": "App published", "score": 1.0},
    {"label": "Merchant trials it", "score": 1.8},
    {"label": "Merchant authorizes", "score": 1.9, "why": "First real user"},
    {"label": "Merchant upgrades", "score": 0.5},
    {"label": "Merchant hits a problem", "score": -1.8, "fix": "Health signals", "fix_score": 0.2},
    {"label": "Merchant uninstalls", "score": -2.0},
    {"label": "Deletes merchant data", "score": -1.2}
  ]
}
```

How to read it:
- From "Merchant trials it" onwards the steps are the merchant's actions, plotted on the developer's feelings. Label them that way so the actor switch is obvious.
- In practice, app review rejections are a major developer pain, so that dip is drawn deep.

## 9. Learning crochet with today's tools

```json
{
  "title": "Learning crochet today (no new app)",
  "persona": "Adult beginner who has never crocheted",
  "jtbd": "Make a first finished crochet piece",
  "trigger": "Sees someone's crochet work and wants to try",
  "scenario": "Self-taught with YouTube and online shopping",
  "success": "A finished first piece that looks like the tutorial",
  "steps": [
    {"label": "Wants to learn crochet", "score": 1.0},
    {"label": "Searches YouTube", "score": 0.3},
    {"label": "Too many videos to pick", "score": -0.8, "fix": "One beginner path", "fix_score": 0.6},
    {"label": "Finds a good tutorial", "score": 1.0},
    {"label": "Notes materials on paper", "score": 0.2},
    {"label": "Leaves to buy on Amazon", "score": -0.6},
    {"label": "Materials arrive", "score": 0.8},
    {"label": "Crochets, pausing video", "score": -0.5},
    {"label": "Stuck on a stitch", "score": -1.6, "fix": "Project checklist", "fix_score": 0.3},
    {"label": "Compares with the video", "score": -0.4},
    {"label": "Finishes first piece", "score": 1.8, "why": "I made this"}
  ]
}
```

How to read it:
- Map the existing journey, not your planned app. A first draft mapped the app the learner wanted to build, and it had almost no dips: you don't draw pain into your own solution.
- The pain is fragmentation (videos, lists, shops, practice). Going one level down, the real product is a learning checklist that works for crochet today and cooking or makeup tomorrow.

## 10. Making a first investment

```json
{
  "title": "Making a first investment",
  "persona": "Salaried professional new to markets",
  "jtbd": "Start growing savings without losing sleep",
  "trigger": "A friend talks about the gains he made",
  "scenario": "First stocks via an investing app",
  "success": "Invested, understands the holdings, stays calm through a market dip",
  "steps": [
    {"label": "Friend shares his gains", "score": 1.0},
    {"label": "Asks friend questions", "score": 0.8},
    {"label": "Scattered research online", "score": -1.0, "fix": "Curated basics", "fix_score": 0.4},
    {"label": "Downloads app, opens account", "score": 0.5},
    {"label": "Makes first investment", "score": -1.5, "fix": "Guided first buy", "fix_score": 0.3},
    {"label": "Checks portfolio daily", "score": -0.5},
    {"label": "Market drops", "score": -1.8, "fix": "Context on drops", "fix_score": -0.4},
    {"label": "Rides out a few cycles", "score": 1.2, "why": "Confidence builds"}
  ]
}
```

How to read it:
- When three people drew their own curves over this map, the first investment was anxiety for one, excitement for another and relief for a third. Disagreement like that reveals segments: finance runs on fear and hope.
- Make the start person-specific ("Friend shares his gains"), not generic ("Interest is generated").

## 11. Rescuing an injured puppy

```json
{
  "title": "Rescuing an injured puppy",
  "persona": "Passer-by who finds an injured street animal",
  "jtbd": "Get the animal safe care fast, and know it recovered",
  "trigger": "Finds an injured puppy on the street",
  "scenario": "Searches and coordinates with NGOs alone",
  "success": "An NGO picks up quickly and shares updates until recovery",
  "steps": [
    {"label": "Finds an injured puppy", "score": -1.0},
    {"label": "Takes photos, location", "score": -0.5},
    {"label": "Googles nearby NGOs", "score": -1.0, "fix": "Best-fit NGO match", "fix_score": 0.5},
    {"label": "Calls NGO after NGO", "score": -1.8, "fix": "One request to all", "fix_score": 0.4},
    {"label": "One NGO agrees", "score": 1.2, "why": "Help is coming"},
    {"label": "Coordinates pickup", "score": 0},
    {"label": "No updates for 20 days", "score": -1.8, "fix": "Status updates", "fix_score": 0.8},
    {"label": "Feels distrust", "score": -1.5}
  ]
}
```

How to read it:
- A life journey with no product yet. Map it before writing a PRD; one map replaces six pages.
- The journey ends below the line. The biggest emotional dip isn't the search, it's the silence after handover, which is easy to miss if you only map up to "NGO agrees".

## 12. Hindi clerk chatbot

```json
{
  "title": "Hindi clerk bot: asking about a report",
  "persona": "Office worker who wants replies in Hindi",
  "jtbd": "Find out where a report stands, in my language",
  "trigger": "Deadline for a report is coming up",
  "scenario": "Chat with a bot whose system prompt says 'Hindi clerk'",
  "success": "A useful answer, always in Hindi script, whatever language I type in",
  "steps": [
    {"label": "Asks where the report is", "score": 0.5},
    {"label": "Bot replies in English", "score": -1.4, "fix": "Hindi-only rule", "fix_score": 0.6},
    {"label": "Retypes with typos", "score": 0.2},
    {"label": "Bot understands typos", "score": 1.4, "why": "Gets my typos"},
    {"label": "Bot replies in Hinglish", "score": -1.5, "fix": "Devanagari rule", "fix_score": 0.9},
    {"label": "Bot replies in Hindi", "score": 1.8, "why": "Speaks my language"}
  ]
}
```

How to read it:
- In AI products, steps are conversation turns and dips are bad answers.
- Each fix is one line added to the system prompt, kept only if an eval confirms it worked. That loop (map, prompt, eval) is the core AI PM job.

## 13. Santra.com shopping assistant

```json
{
  "title": "Santra.com assistant: is this top right for work?",
  "persona": "Sarah, 32, anxious first-time online shopper, budget $150",
  "jtbd": "Buy professional clothing for work presentations with confidence",
  "trigger": "Has presentations coming up and nothing suitable to wear",
  "scenario": "Asks the assistant about one item by its clothing ID",
  "success": "A personal answer that names her concerns, uses real reviews and gives a buy link",
  "steps": [
    {"label": "Opens the assistant", "score": 0.5},
    {"label": "Asks about item 1094", "score": 0.8},
    {"label": "Bot: no access to IDs", "score": -1.6, "fix": "Catalogue tool", "fix_score": 0.6},
    {"label": "Gets generic tips", "score": -1.0, "fix": "Ground in reviews", "fix_score": 0.8},
    {"label": "No buy link offered", "score": -0.8, "fix": "Add buy link", "fix_score": 1.0},
    {"label": "Concerns ignored", "score": -1.2, "fix": "Use her profile", "fix_score": 1.2},
    {"label": "Leaves to read reviews", "score": -1.5}
  ]
}
```

How to read it:
- Every dip is an AI response-quality issue: the bot isn't connected to the data (no tool) and isn't personalised.
- Each fix becomes an eval check: the answer has a buy link; it mentions Sarah by name and at least one of her concerns. If a check passes when the answer clearly fails, the check itself is wrong (a false pass).

## 14. Telecom support chatbot

```json
{
  "title": "Telecom support: reaching a human",
  "persona": "Adult child helping an elderly parent with a phone issue",
  "jtbd": "Get the parent's phone problem fixed",
  "trigger": "The parent's service stops working properly",
  "scenario": "Tries phone support, then chat",
  "success": "Issue understood and fixed in one contact",
  "steps": [
    {"label": "Service stops working", "score": -0.5},
    {"label": "Calls support line", "score": -0.3},
    {"label": "Routed to AI bot", "score": -0.8},
    {"label": "Tries chat instead", "score": -0.6},
    {"label": "Same bot again", "score": -1.3, "fix": "Human handoff", "fix_score": 0.5},
    {"label": "Parent can't explain", "score": -1.8, "fix": "Own-language voice", "fix_score": 0.4},
    {"label": "Gives up, unresolved", "score": -2.0}
  ]
}
```

How to read it:
- A whole journey below the line: AI used to deflect rather than help.
- The dip is about trust and access, not answer quality. The fix is a human in the loop, plus meeting the user in their own language.
