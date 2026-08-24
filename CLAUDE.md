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
| Home | Live (partial) | Summary/front-page panel, first in the deck. Weather tile is live; tasks/workout/headlines/stocks tiles are honest empty states until those sources exist |
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

**Design system (light, warm, "premium personal command centre"):** the
dashboard deliberately moved off the original dark instrument-panel look to
a light/warm palette — `--bg`/`--surface`/`--border`/`--text`/`--muted`/
`--faint` for the neutrals, `--accent` as the primary muted-green system
accent, and one `--c-<domain>` hex per subject area (weather, running,
workouts, fitness, coffee, stocks). Content sits in `.card` blocks (white
surface, subtle border, soft shadow, `--radius`) rather than bare full-bleed
panels. A handful of accent tokens are **reserved but unused** —
`--c-padel`, `--c-productivity`, `--c-boardgames`, `--c-stats` — for
domains the owner wants eventually (padel, projects/productivity, board
games, stats-flavored content) but that have no data source yet. Reuse a
reserved token when one of those panels finally gets built rather than
inventing a new hex; don't build the panel itself until its data source is
decided (see "Open questions" below). Keep to this palette family for
anything new — no gradients, minimal animation (the pulsing status dot is
about the ceiling), thin single-weight stroke SVG icons (no emoji) per
panel eyebrow.

**Home panel:** first panel in the deck (`data-name="home"`), an editorial
front-page-style summary — masthead (date + live weather), then a 3-card
row for Today/tasks+workout, Headlines, and Stocks. It's a glance layer
only; tapping/swiping into a domain's own panel is still where the detail
lives. Its tiles mirror whatever the domain's own panel status is — don't
fake data in a Home tile that the domain panel itself doesn't have yet.

**Personality details (deliberate, keep consistent on new panels):**
- Two Google Fonts loaded in `<head>`: `Newsreader` (the `--display`
  token — italic serif for headline moments: masthead date, weather
  condition text, coffee bean names, Home's lead headline) and
  `IBM Plex Mono` (front of the `--mono` stack). Data/labels stay mono;
  editorial/journal moments get the serif. Don't add a third typeface.
- Every panel eyebrow icon sits in a `.badge` — a small circle tinted at
  15% of that panel's accent color (`color-mix(in srgb, var(--accent)
  15%, transparent)`), not a bare icon. New panels should follow this.
- Every panel has a large (300px), very low-opacity (~10%) ghost-icon
  `.watermark` — same icon as the badge, vertically centered on the
  right edge — so empty/not-wired panels read as designed negative
  space rather than blank. **Gotcha:** `.panel` needs `position:relative`
  *and* `z-index:0` together, or the watermark's `z-index:-1` escapes to
  a stacking context above `.panel` and renders behind the panel's own
  background (invisible). Don't drop the `z-index:0`.
- `.panel` has a faint dot-grid background (`radial-gradient(var(--border)
  1px, transparent 1px)`) — a graph-paper nod to the "statistician who
  loves data" personality brief. Keep it subtle; it's texture, not a
  focal element.
- The Home "Today" card has an SVG ring showing task completion
  (`stroke-dasharray` trick, `--accent` colored). If task data becomes
  real, recompute the dasharray from the real fraction rather than
  hardcoding.
- Avoid the generic-AI-dashboard tropes this system deliberately steered
  away from: no gradients, no left-border-accent cards, no emoji as
  icons (SVG stroke icons only), minimal animation (the pulsing
  status-dot on live panels is about the ceiling).

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
- **Home panel's Today/Headlines/Stocks tiles:** no source decided for
  tasks, news, or the Home stocks summary either — same "ask before
  building" rule applies. Don't wire these to fake/hardcoded data; they stay
  honest empty states until a real source is picked.
- **Aspirational domains (padel, productivity/projects, board games,
  stats-flavored content):** these came out of a design-personality brief,
  not a build request. Accent tokens are reserved (see design system note
  above) but no panel, data source, or ingestion pattern exists — don't
  start building one without the owner picking it explicitly, the way
  Running/Stocks/Fitness already went through this "ask before building"
  gate.

## File/deliverable conventions

- All deliverables committed to this repo, root or the relevant subfolder —
  never left only in a chat scratchpad.
- Commit messages: short, imperative, e.g. `"Add coffee panel"` (see git log
  for existing style).
- `README.md` is the *owner-facing* setup/install guide (repo push, Pages,
  iPad, Shortcuts) — this file (`CLAUDE.md`) is the *assistant-facing*
  architecture/convention brief. Keep them separate; update both if a change
  affects both.
