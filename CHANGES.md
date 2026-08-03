# WDS v1 — Iteration 1: Frontend Modernization — CHANGES

This iteration is a frontend-only redesign. All existing backend
functionality (auth, SQLite/SQLAlchemy models, YOLOv5 detection,
upload flow, camera streaming, detection history) works exactly as
it did before, through the same routes.

## Design direction

Dark-first "operations console" theme (mint/cyan for scanning &
safety, red for threats, amber for warnings), with a recurring
camera-viewfinder "reticle" corner-bracket motif on cards, tying the
UI back to the product's subject matter. Typography: Space Grotesk
(display), Inter (body), JetBrains Mono (data/timestamps/badges).

## Files modified / added

### Backend (1 small, documented change)
- **`app.py`** — the `/dashboard` route now also queries the 5 most
  recent `Detection` rows and passes them to the template as
  `recent`, to power the new "Recent Detections" panel. This uses
  the existing `Detection` model/table only — no schema changes, no
  new routes, no change to any other route's behavior. Everything
  else in `app.py` is byte-for-byte the same as before.

No changes were made to `db_models.py`, `detector.py`, `camera.py`,
`requirements.txt`, or `weights/best.pt`.

### Templates (all rewritten, same routes/forms/fields preserved)
- `templates/base.html` — **new**. Shared layout: navbar, footer,
  mobile drawer, toast container, confirm-dialog markup, script
  includes. All other pages extend this.
- `templates/home.html`
- `templates/login.html`
- `templates/signup.html`
- `templates/dashboard.html`
- `templates/upload.html`
- `templates/camera.html`
- `templates/history.html`

All forms keep their original `name` attributes, `method`, and
`enctype` so the existing Flask handlers work unmodified. Flask's
built-in `session` context variable (available in every Jinja
template automatically) is used to conditionally show/hide
logged-in vs. logged-out navigation — this required no backend code.

### CSS (new, replaces the old single `main.css`)
```
static/css/
├── variables.css   design tokens (color, type, spacing, shadows)
├── main.css        font import, reset, base typography, imports the rest
├── layout.css       containers, navbar, footer, section/grid helpers
├── components.css   cards, buttons, inputs, badges, toasts, modals, tables
├── responsive.css   breakpoints for laptop/tablet/mobile
├── auth.css         login/signup split layout
├── dashboard.css     stat cards, threat ring, recent list, quick actions
├── upload.css       dropzone, preview, result cards
├── history.css       toolbar, pagination, table cell styles
└── camera.css        radio panel, live feed frame, reticle overlay
```
No `<style>` tags remain in any template. Inline `style=""`
attributes are used **only** for genuinely dynamic, data-driven
values that can't be static CSS (confidence-bar fill widths and the
threat-level ring's SVG stroke offset, computed per row from the
database). Everything else uses classes.

### JavaScript (new — presentational only, no backend calls)
```
static/js/
├── main.js      mobile nav, dark/light theme toggle, toast notifications
│                (rendered from Flask's flash() messages), confirm
│                dialogs, button loading states, active-nav highlighting
├── auth.js      login/signup client-side validation, password
│                match check, show/hide password
├── upload.js    drag & drop, image preview, remove/reset, submit guard
├── history.js   client-side search, column sort, pagination
└── camera.js    IP camera field toggle, live-feed placeholder/
                 start-stop control
```
None of this JS talks to any new endpoint. `upload.js` still submits
the real multipart form to `/upload`; `history.js`/`upload.js`/
`camera.js` only manipulate what the server already rendered.

## Assumptions made
1. **Result-image filename convention.** The upload route saves
   detection renders as `static/results/result_<original filename>`.
   The dashboard's "Recent Detections" thumbnails and the history
   table's thumbnails reconstruct this path in the template
   (`results/result_` + `filename`) rather than via a new DB column.
   If a result image is missing (e.g. very old rows, or rows created
   outside the upload flow), the `<img>` is hidden gracefully via
   `onerror` — no broken-image icon.
2. **Threat vs. safe styling.** Rows/values are treated as "safe"
   when `threat` (case-insensitive) equals `"none"`, and "threat"
   otherwise. This matches the existing dashboard route's `"None"`
   default when there are no detections yet.
3. **Live camera feed on page load.** The original `<img src="{{
   url_for('video_feed') }}">` would start streaming immediately on
   page load. The redesign instead shows a "Start Live Feed" button
   and only requests `/video_feed` when clicked, with a friendly
   placeholder if the stream errors (no webcam in this environment,
   per the README). The route and streaming mechanism are unchanged
   — this is purely about *when* the browser requests it.
4. **Confidence formatting.** `Detection.confidence` is stored as a
   0–1 float; templates multiply by 100 for display, matching the
   existing `app.py`/original templates' convention.
5. **Sort default on Detection History** is newest-first, matching
   the existing `/history` route's `order_by(Detection.timestamp.desc())`.

## Requires manual testing
- **Live camera streaming** — this environment (and the original
  Codespaces dev environment, per the README) has no webcam, so the
  "Start Live Feed" → `/video_feed` flow and the IP-camera URL path
  could not be exercised end-to-end. Please verify on a machine with
  camera access.
- **Full request/response cycle** — templates were validated by
  direct Jinja rendering (all render without error) and by static
  analysis (Python `py_compile`, Node `--check` on all JS, CSS brace
  balance). The full Flask app could not be run in this sandbox
  because `torch`/YOLOv5 aren't installed here and there's no
  network access to install them. Please do a normal `flask run`
  smoke test of signup → login → upload → history → camera → logout.
- **Toast message classification.** `main.js` guesses whether a
  flashed message is an error vs. success by matching keywords
  (e.g. "invalid", "already exists") against the existing flash
  strings in `app.py`. If you add new `flash()` messages later,
  double-check they still get the right toast color, or pass a
  category explicitly.
- **Cross-browser drag & drop** on the upload page (tested logically,
  not in an actual browser).
- **Responsive layout** at real device widths/orientations — built
  to the breakpoints in `responsive.css` but not visually verified
  on physical devices.
