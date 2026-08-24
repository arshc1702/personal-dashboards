# Panel — project context

Read this before making changes. It's the standing brief for whichever
session is working on this repo — treat it as the source of truth over
anything remembered from a prior chat.

## What this is

An always-on personal dashboard for a spare iPad: six full-screen swipeable
panels (Weather, Running, Workouts, Fitness, Coffee, Stocks), installed as a
PWA, with tap-to-talk voice nav and Siri Shortcut deep-links. Single static
site, no framework, no server. Owner does not write code — all changes are
authored by Claude, reviewed by the owner as diffs/screenshots before pushing.

**Repo:** `github.com/arshc1702/personal-dashboards` (public — see "Why
public" below)
**Live URL:** `https://arshc1702.github.io/personal-dashboards/`
**Plan:** GitHub Free (personal account)

## Current state

| Panel | Status | Data source |
|---|---|---|
| Weather | Live | Open-Meteo, no auth, Action every 15 min |
| Coffee | Live | GitHub Issue form → Action parses → `data/coffee.json` |
| Running | Not built | Strava API — needs OAuth app registration |
| Stocks | Not built | IBKR web API or a free quote feed — needs credentials |
| Workouts | Not built | No tracker exists — likely same issue-form pattern as Coffee |
| Fitness | Not built | Source undecided — see open questions below |

iPad install itself is deferred — instructions exist in `README.md` but the
owner hasn't done the physical setup yet. Don't assume it's done.

## Architecture

**Two ingestion patterns are established — use one of these, don't invent a
third without discussing it first:**

1. **Scheduled pull** (Weather, and planned for Running/Stocks): a GitHub
   Action on a cron writes `data/<panel>.json`. Frontend fetches that file
   with `cache:'no-store'` on load + every 5 min. See
   `.github/workflows/update-weather.yml` + `scripts/fetch_weather.py` as the
   template — copy this pattern, including the "commit only if changed" step.
2. **Manual log via GitHub Issue form** (Coffee, and likely Workouts): an
   issue-form template in `.github/ISSUE_TEMPLATE/`, an Action triggered on
   `issues: opened` filtered by label, a Python parser reading
   `GITHUB_EVENT_PATH` (never the raw env var — issue bodies can contain
   characters that break shell escaping), appends to the JSON, closes the
   issue. See `.github/workflows/log-coffee.yml` +
   `scripts/log_coffee.py` as the template.

**Frontend:** everything lives in one `index.html` — CSS custom properties
in `:root` define the whole design system (colors, fonts). New panels must
reuse these tokens, not introduce new hex values. Panel nav is a horizontal
scroll-snap deck; `#panel-name` hash routing already supports Siri Shortcut
deep-links — reuse it, don't build new routing.

**PWA shell:** `manifest.json` + `sw.js` are already wired for
Add-to-Home-Screen. Don't touch unless a panel needs offline behavior beyond
what's there.

## Privacy tiers — apply automatically, don't ask each time

- **High sensitivity (Strava GPS):** never write raw lat/lon, route
  polylines, or start/end coordinates to any `data/*.json` that ends up in
  the public repo/site. Aggregate only — weekly distance, pace, duration.
- **Medium sensitivity (IBKR):** show % change / performance, never dollar
  values or share counts, unless the owner explicitly asks for a private
  build later.
- **Low sensitivity (weather, coffee, workouts):** no special handling
  needed.
- **Secrets (API keys, OAuth tokens):** GitHub Encrypted Secrets
  (`Settings → Secrets and variables → Actions`) only. Never in a committed
  file, never in a `.env` that gets accidentally tracked — check `.gitignore`
  covers it first.

## Why the repo is public, and what that means

GitHub Free doesn't serve Pages from a private repo (Pro/Team do, but even
then the *published site* is still public-by-URL regardless of plan —
private Pages needs Enterprise). So: repo is public, meaning committed code
and JSON are visible to anyone. This is fine while only Weather/Coffee are
live. **Before Running or Stocks ship real data, revisit this** — either
strip sensitive fields at the aggregation step (preferred, cheap) or add a
Cloudflare Access gate in front of the Pages URL (free tier). Don't ship
Strava/IBKR data assuming the URL is obscure enough — it isn't.

## Edge-case mechanics (don't leave these undefined)

- **Action fails / API is down:** the frontend fetches whatever
  `data/<panel>.json` last committed successfully — it will silently show
  stale data, not an error, since there's no "last updated" staleness check
  yet. This is a known gap, not a design choice — flag it to the owner if
  building a panel where stale-but-silent is actually risky (e.g. stocks).
- **Empty data (no entries logged yet):** established pattern (see Coffee) —
  explicit empty-state copy ("No entries yet — log one via the [X] issue"),
  not a blank panel. New manual-log panels should match this.
- **Issue-form optional field left blank:** GitHub renders `_No response_`
  in the body; the parser must map that to `''`, not the literal string (see
  `log_coffee.py` for the pattern).
- **GitHub Actions minutes:** Free tier is 2,000 min/month. Weather at every
  15 min is trivial cost (~seconds per run). Before adding a high-frequency
  cron (e.g. Stocks every 5 min during market hours), do the rough math
  against the 2,000-min budget — don't assume it's free to just add more
  crons.
- **Voice control:** iOS Safari's Web Speech API requires a tap to start
  listening each time — there is no always-listening mode. The Siri
  Shortcuts + `#hash` deep-link path is the hands-free route; don't try to
  build background listening, it's not possible in this environment.

## Open questions before building the next panels

- **Running:** needs a Strava API app registered by the owner (client
  ID/secret) before OAuth can be wired — this is a manual step only he can
  do, flag it rather than blocking on it silently.
- **Stocks:** IBKR web API vs. a simpler free quote feed — undecided, ask
  before building.
- **Fitness:** may fully overlap with Running (activity load from Strava) or
  be a separate manual/Apple-Health-export source — ask before assuming.

## File/deliverable conventions

- All deliverables committed to this repo, root or the relevant subfolder —
  never left only in a chat scratchpad.
- Commit messages: short, imperative, e.g. `"Add coffee panel"` (see git log
  for existing style).
- `README.md` is the *owner-facing* setup/install guide (repo push, Pages,
  iPad, Shortcuts) — this file (`CLAUDE.md`) is the *assistant-facing*
  architecture/convention brief. Keep them separate; update both if a change
  affects both.
