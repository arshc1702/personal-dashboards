# Panel — personal iPad dashboard

A swipeable, always-on dashboard. One horizontal-scroll page, eight
full-screen sections (home, todos, weather, running, workouts, fitness,
coffee, stocks), tap-to-talk voice navigation, installable as a home-screen
app on the iPad.

**Status:** Home (summary front page), Todos, and Weather are live (Weather
from Open-Meteo, no API key). Coffee is live — log a brew via a GitHub Issue
and it shows up on the panel. The other four panels are stubbed with a note
on what data source they need — see the roadmap at the bottom.

## 1. Push this to your own GitHub repo

I can't create a repo on your account directly, so do this part yourself:

```bash
cd dashboard
git init
git add .
git commit -m "Panel dashboard v1 — weather live"
gh repo create panel --public --source=. --push
# or, without the gh CLI:
# git remote add origin https://github.com/<you>/panel.git
# git branch -M main
# git push -u origin main
```

## 2. Turn on GitHub Pages

Repo → **Settings → Pages** → Source: `Deploy from a branch` → Branch: `main`,
folder `/ (root)`. Your dashboard will be live at
`https://<you>.github.io/panel/` within a minute or two.

The weather Action (`.github/workflows/update-weather.yml`) runs every 15
minutes automatically once it's pushed — no setup needed. You can trigger it
immediately from the **Actions** tab → *Update weather data* → **Run workflow**,
instead of waiting for the first scheduled run.

## 3. Install on the iPad

1. Open `https://<you>.github.io/panel/` in **Safari** on the iPad (must be
   Safari, not Chrome, for the home-screen install to behave as a full app).
2. Share icon → **Add to Home Screen**. This gives you a standalone app with
   no browser chrome, using the dark theme and icon already configured.
3. Launch it from the home screen once so it registers as a PWA.

## 4. Set it up as a fixed display

- **Settings → Display & Brightness → Auto-Lock → Never** (only reasonable
  while it's dedicated to this and plugged in).
- **Settings → Accessibility → Guided Access → On**, set a passcode. Then
  triple-click the side/home button inside the Panel app to lock the iPad
  into just this app — swipes still work, nothing else does.
- Keep it on a charger/stand. An old iPad running one static web app on wifi
  has negligible battery/heat concerns left on indefinitely.

## 5. Voice control

Two layers, because iOS won't let a web page listen in the background:

- **In-app tap-to-talk** — the mic button (bottom-right) uses the Web Speech
  API. Tap it, say "weather", "stocks", "running", "next", "back", etc. Works
  immediately, no setup, but needs a tap first each time.
- **Hands-free via Siri (recommended for a wall-mounted display)** — in the
  **Shortcuts** app, create one shortcut per panel:
  - Action: *Open URLs* → `https://<you>.github.io/panel/#stocks`
  - Add a custom Siri phrase, e.g. "Show my stocks"
  - Repeat for `#home`, `#todos`, `#weather`, `#running`, `#workouts`, `#fitness`, `#coffee`

  Now "Hey Siri, show my stocks" opens straight to that panel — the `#name`
  hash routing is already built into `index.html`.

## 6. Connect Todos so you can add/check off tasks

Viewing the Todos panel needs nothing — it reads GitHub Issues from the
public repo directly. **Adding or completing a task needs a token**, once
per device (iPad, phone, laptop — wherever you'll actually add tasks from):

1. On GitHub: **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token**.
2. **Repository access** → *Only select repositories* → pick
   `personal-dashboards`. Don't grant access to any other repo.
3. **Permissions → Repository permissions → Issues** → set to
   *Read and write*. Leave everything else at *No access*.
4. Set an expiration (a year is fine for a personal, single-repo token) and
   generate it. Copy the token — GitHub only shows it once.
5. On the device, tap **connect** next to the TODOS label (or just tap any
   checkbox/add field — it'll prompt automatically) and paste the token in.
   It's saved in that device's browser storage only; you'll do this once per
   device, not once per session.

Why fine-grained and scoped this tightly: the token lives in browser
storage on a personal device, not a vetted secrets manager, so it's worth
limiting what it can touch if that device is ever lost or compromised — it
can only open/close issues on this one repo, nothing else on your GitHub
account.

## Roadmap — wiring up the remaining panels

Each panel needs its own scheduled Action (copy `update-weather.yml` as the
template) that writes a `data/<name>.json` file, plus a small render function
in `index.html` mirroring `loadWeather()`.

| Panel | Data source | Notes |
|---|---|---|
| Running | Strava API | OAuth needed once; Action refresh every ~30 min is plenty |
| Stocks | IBKR web API or a free quote feed | Consider a faster interval (5 min) only during market hours to save Action minutes |
| Workouts | `data/workouts.json`, hand-edited or Siri Shortcut → GitHub API commit | No existing tracker — this file *is* the tracker |
| Fitness | Strava (load/recovery) or an Apple Health export | Decide scope once running is wired up — may overlap |

Home's Headlines/Stocks tiles are also unwired — same rule, pick a
source before building. (Today is done — it mirrors the Todos panel.)
Coffee is done: it's a GitHub Issue form
(`.github/ISSUE_TEMPLATE/coffee-log.yml`) → `scripts/log_coffee.py` →
`data/coffee.json`. To log a brew, open a new issue from that template on
the repo; it appends to the log and shows up on the panel within a minute.

Say the word and I'll build the next panel end-to-end (Action + JSON schema +
render function) the same way weather and coffee were done.
