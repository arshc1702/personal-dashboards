# Panel — project context

Read this before making changes. It's the standing brief for whichever
session is working on this repo — treat it as the source of truth over
anything remembered from a prior chat.

## What this is

An always-on personal dashboard for a spare iPad: full-screen swipeable
panels (Home, Todos, Coffee, Weather, Running, Workouts, Fitness, Stocks),
installed as a PWA, with tap-to-talk voice nav and Siri Shortcut deep-links.
Single static site, no framework, no traditional server (Todos writes
directly to the GitHub API from the browser — see Architecture — but there
is still no backend Claude or the owner has to run). Owner does not write
code — all changes are authored by Claude, reviewed by the owner as
diffs/screenshots before pushing.

**Repo:** `github.com/arshc1702/personal-dashboards` (public — see "Why
public" below)
**Live URL:** `https://arshc1702.github.io/personal-dashboards/`
**Plan:** GitHub Free (personal account)

## Current state

| Panel | Status | Data source |
|---|---|---|
| Home | Live (partial) | Summary/front-page panel, first in the deck. Weather tile and Today (todos) tile are both live; workout/headlines/stocks tiles are honest empty states until those sources exist |
| Todos | Live | GitHub Issues, read live client-side + written directly from the panel via an on-device token — see Architecture pattern 3 |
| Coffee | Live | Bean catalog, same pattern 3 as Todos (GitHub Issues + on-device token). Drag-and-drop between Specialty/House Blend, click a card for a detail modal. See Coffee panel note below |
| Weather | Live | Open-Meteo, no auth, Action every 15 min. Also carries a 6-hour hourly forecast (`data.hourly`) for the panel's trend strip |
| Running | Not built | Strava API — needs OAuth app registration |
| Stocks | Not built | IBKR web API or a free quote feed — needs credentials |
| Workouts | Not built | No tracker exists — likely same issue-form pattern as Coffee |
| Fitness | Not built | Source undecided — see open questions below |

iPad install itself is deferred — instructions exist in `README.md` but the
owner hasn't done the physical setup yet. Don't assume it's done.

## Architecture

**Three ingestion patterns are established — use one of these, don't invent
a fourth without discussing it first:**

1. **Scheduled pull** (Weather, and planned for Running/Stocks): a GitHub
   Action on a cron writes `data/<panel>.json`. Frontend fetches that file
   with `cache:'no-store'` on load + every 5 min. See
   `.github/workflows/update-weather.yml` + `scripts/fetch_weather.py` as the
   template — copy this pattern, including the "commit only if changed" step.
2. **Manual log via GitHub Issue form** (likely Workouts): an
   issue-form template in `.github/ISSUE_TEMPLATE/`, an Action triggered on
   `issues: opened` filtered by label, a Python parser reading
   `GITHUB_EVENT_PATH` (never the raw env var — issue bodies can contain
   characters that break shell escaping), appends to a `data/*.json` file,
   closes the issue. No current panel uses this pattern anymore (Coffee
   used to — see below — and was migrated off it); the closest reference
   left in history is the git log around the original Coffee build. Still a
   valid pattern for a panel that's genuinely append-only and never needs
   editing/recategorizing from the dashboard itself.
3. **Interactive write via GitHub Issues + on-device token** (Todos and
   Coffee): each record is a GitHub Issue, categorized by label, read live
   and written directly from the panel. Reads (`GET /issues?labels=...`)
   are unauthenticated — the repo is public, so any device can view either
   panel with zero setup. Writes go straight from browser JS to
   `api.github.com`, authenticated with a personal access token the owner
   pastes in once per device (`prompt()`-based `ensureToken()` flow in
   `index.html`, stored in that device's `localStorage` under
   `panel_gh_token` — **never** committed anywhere, and **shared** across
   both panels — one token, one `connect` action, covers Todos and Coffee).
   **Security posture:** only ever tell the owner to use a **fine-grained
   PAT scoped to just this one repo, Issues: Read and write permission
   only** — never a classic PAT with broad `repo` scope, since the token
   lives in browser storage on a personal device, not a vetted secrets
   store. **Resilience gotcha:** `loadTodos()` and `loadCoffeeBeans()` both
   retry once, unauthenticated, on a 401 — an expired/bad token must only
   break the write path (add/complete/recategorize), never the read-only
   viewing experience across other devices. Keep that fallback if you touch
   either function. This pattern is the right fit *only* when the panel
   genuinely needs add/edit/move from the dashboard itself — for anything
   append-only, pattern 2 (Issue form) is simpler and needs no client-side
   token at all.
   - **Todos:** each task = one issue (open=active, closed=done), tagged
     `todo` + `category:<x>`. Add = `POST /issues`. Complete = `PATCH
     /issues/{n}` with `state:closed`.
   - **Coffee:** each bean = one issue (always left open — a bean doesn't
     "complete"), tagged `coffee-bean` + `blend:specialty` or
     `blend:house`. New beans always come in via the
     `coffee-bean.yml` issue form (richer fields than a quick client-side
     add — name, roaster, origin, dose/yield/time, notes, and an image
     dragged into the form's body, which GitHub auto-hosts and which
     `extractImageUrl()` pulls out of the issue body via regex on the
     rendered markdown `![...](url)`). Recategorizing (drag between
     Specialty/House on the panel) is the only client-side write, via
     `PATCH /issues/{n}` — and it **replaces the full labels array**
     (`[coffee-bean, blend:<target>]`), not an additive patch, because
     GitHub's API has no "add/remove one label" verb on this endpoint.
     That's fine only because bean issues are constructed to carry
     exactly these two labels and nothing else — never add a third label
     to a bean issue expecting it to survive a drag.

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
workouts, fitness, coffee, stocks, plus `--c-padel`/`--c-productivity`/
`--c-lifeadmin` for the Todos categories). Content sits in `.card` blocks
(white surface, subtle border, soft shadow, `--radius`) rather than bare
full-bleed panels. `--c-boardgames` and `--c-stats` are still **reserved
but unused** — for a future dedicated board-games panel and
stats/analytics-flavored content respectively. Note `--c-padel` and
`--c-productivity` are now in use by Todos' category labels, but that's
*not* the same as a dedicated Padel or Productivity panel existing — if
the owner later wants a real padel-match-tracking panel (scores, opponents,
etc.) or a projects panel, that's still new scope, reuse the same token,
don't invent a new hex. Keep to this palette family for anything new — no
gradients, minimal animation (the pulsing status dot is about the ceiling),
thin single-weight stroke SVG icons (no emoji) per panel eyebrow.

**Home panel:** first panel in the deck (`data-name="home"`), an editorial
front-page-style summary — masthead (date + live weather), then a 3-card
row for Today/tasks+workout, Headlines, and Stocks. It's a glance layer
only; tapping/swiping into a domain's own panel is still where the detail
lives. Its tiles mirror whatever the domain's own panel status is — don't
fake data in a Home tile that the domain panel itself doesn't have yet. The
Today tile is wired to the same `loadTodos()` data as the Todos panel
(total open count + a short preview, not a completion ring — there's no
"due today" concept in the Issues-backed model, so don't reintroduce one
without a real due-date field); the Workout sub-section stays an honest
empty state until a workout-plan source exists.

**Todos panel's "ledger" pattern (deliberate, keep on new categories):**
each category card shows its **oldest open issue as a "Next up" hero**
(`.todo-hero`, Newsreader italic, a `NEXT UP · <age>` mono tag in the
category accent) and the rest as a compact list below a hairline — sorted
oldest-first, so hierarchy reflects a real signal (what's been waiting
longest), not arbitrary emphasis. Every row carries a `timeAgo(created_at)`
age tag for the same reason. The add-field is a ledger-style underline
(`.todo-add`, transparent background, border-bottom only), not a boxed
input — matches the journal/editorial voice, don't revert to a boxed field.
Completing a task is optimistic: `.checking` plays a drawn-in checkmark +
strikethrough (~220ms), `.leaving` fades the row out (~240ms), *then* the
local cache is updated and the GitHub PATCH fires in the background — the
UI never waits on the network. If that PATCH fails, it alerts and calls
`loadTodos()` to reconcile with reality rather than trusting the optimistic
state. Keep this order (animate → mutate local state → network) if you
touch this code; don't make it synchronous again.

**Coffee panel (bean catalog, replaced the old brew-journal concept
entirely — don't resurrect "log a brew"):** two drag-and-drop grids,
Specialty Blend and House Blend, plus a `coffee-setup` spec row at top read
from `data/coffee-setup.json` (a small hand-edited array of `{label,
value}` — machine, grinder, water, whatever gear is worth showing; edit
that file directly, it's not wired to any Action or issue form since it
changes rarely). Bean data comes from GitHub Issues, see Architecture
pattern 3. A few things worth knowing before touching this:
- **Drag-and-drop is hand-rolled on Pointer Events, not native HTML5
  DnD.** The `draggable` attribute's DnD API does not work reliably on iOS
  Safari touch — this is a real device constraint, not a style choice.
  `attachBeanCardHandlers()` in `index.html` tracks `pointerdown` →
  `pointermove` (crosses a ~10px threshold before it counts as a drag,
  otherwise a plain tap opens the detail modal) → `pointerup`
  (`elementFromPoint` under the pointer, with the dragged card's own
  `pointer-events` set to `none` for that one lookup so it doesn't occlude
  itself, decides which `.bean-grid` it was dropped on). Keep this
  approach for any future drag interaction in this app — don't swap in
  native `draggable` and assume it'll work on the iPad.
- **Card face vs. detail modal:** the card shows name/roaster/recipe only;
  tapping opens `#bean-modal-backdrop` with the full image, origin, the
  dose/yield/time plus an auto-computed ratio (`ratioString()` — never ask
  the user to type a ratio, derive it), and notes. Keep that split — don't
  cram everything onto the card face.
- **Images are never uploaded by this codebase.** There's no upload
  endpoint. A bean's image is whatever GitHub-hosted URL shows up in the
  issue body (the owner drags a photo into the issue form's Image field on
  github.com and GitHub auto-hosts it); `extractImageUrl()` just regexes
  the first markdown image link out of the body. No image present → the
  card/modal shows the plain cup-icon placeholder, not a broken `<img>`.

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
- **On design inspiration from templates (Notion, dashboard galleries,
  etc.):** the owner may point at these for ideas — treat them as a source
  of *structural* widget idioms (stat tiles, progress rings, activity
  heatmaps, sparklines) worth translating, never a look to copy wholesale.
  Redraw everything in this system's own tokens/typography (serif+mono,
  warm neutrals, thin stroke icons). Do not adopt pastel gradients, photo
  collages, or dense cutesy widget grids just because a referenced
  template uses them — that's the "generic Notion clone" this dashboard
  was explicitly built to not be.
- **Mocking panels that have no data source yet:** don't put fabricated
  numbers into `index.html` for an unbuilt panel — that violates the
  "no fake data" rule for the *live* site. If a design pass is wanted for
  those (see Running/Workouts/Fitness/Stocks precedent), build it as a
  separate concept Artifact using the same tokens, clearly labeled as a
  preview, and leave the live panel as an honest empty state until a real
  source is picked.

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
- **Secrets (API keys, OAuth tokens) used by Actions:** GitHub Encrypted
  Secrets (`Settings → Secrets and variables → Actions`) only. Never in a
  committed file, never in a `.env` that gets accidentally tracked — check
  `.gitignore` covers it first.
- **The Todos panel's GitHub token is different and deliberately so:** it's
  entered client-side and lives in a specific device's browser
  `localStorage`, never in the repo or an Action secret — it has to be
  reachable from the browser to make authenticated write calls. Only ever
  advise a fine-grained PAT scoped to this one repo's Issues permission
  (see Architecture pattern 3). Don't "fix" this by trying to move it into
  Actions secrets — that would require a server-side proxy, which is a
  bigger architecture change to discuss first, not a drop-in swap.

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
- **Empty data (no entries logged yet):** established pattern (see Coffee's
  bean grids, Todos' category lists) — explicit empty-state copy ("No beans
  yet — add one via the [X] issue"), not a blank panel. New panels should
  match this.
- **Issue-form optional field left blank:** GitHub renders `_No response_`
  in the body; any body parser must map that to `''`, not the literal
  string (see `parseIssueField()` in `index.html`, used by the Coffee
  panel, for the client-side JS version of this same rule).
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
- **Home panel's Headlines/Stocks tiles:** no source decided for news or
  the Home stocks summary — same "ask before building" rule applies. Don't
  wire these to fake/hardcoded data; they stay honest empty states until a
  real source is picked. (Today tile is resolved — see Home panel note
  above.)
- **Coffee setup specs and initial beans:** `data/coffee-setup.json` ships
  as an empty array and no bean issues exist yet — both need real content
  from the owner (gear list; bean name/roaster/recipe/image per bean via
  the issue form). Don't invent placeholder gear or beans into the live
  data — ask, same as any other empty-state panel.
- **Aspirational domains still open (board games, stats-flavored content):**
  these came out of a design-personality brief, not a build request. Accent
  tokens are reserved (see design system note above) but no panel, data
  source, or ingestion pattern exists — don't start building one without
  the owner picking it explicitly. (Padel and productivity are partially
  resolved — they exist as Todos categories now — but a dedicated
  match-tracking/projects panel for either is still open, same gate.)

## File/deliverable conventions

- All deliverables committed to this repo, root or the relevant subfolder —
  never left only in a chat scratchpad.
- Commit messages: short, imperative, e.g. `"Add coffee panel"` (see git log
  for existing style).
- `README.md` is the *owner-facing* setup/install guide (repo push, Pages,
  iPad, Shortcuts) — this file (`CLAUDE.md`) is the *assistant-facing*
  architecture/convention brief. Keep them separate; update both if a change
  affects both.
