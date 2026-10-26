# Claudy Day

A single-file page (`index.html`, no build step) that turns Claude Code token usage into cups of water.
Double-click `Claudy Day.cmd` (or run `python serve.py`): it starts a local server and opens
http://localhost:8765/ with your live numbers. Opening `index.html` directly jumps to that server when it
is running, otherwise shows the saved/screenshot numbers. Fonts load from Google Fonts; everything else is inline.

## How it's put together
- **Estimate** (`water()`): energy per 1,000 tokens (0.96 Wh output, 0.32 input, 0.40 cache write,
  0.032 cache read) + 10% overhead, times 3.6 mL/Wh (or 1.15 mL/Wh "cooling only"); 1 cup = 236.6 mL.
- **Data**: `serve.py` serves `~/.claude/stats-cache.json` (or `$CLAUDE_CONFIG_DIR`) at `./stats-cache.json`,
  read fresh per request, trimmed to `lastComputedDate` + `modelUsage`, only on 127.0.0.1 (`--no-open` skips
  opening a browser; a second launch just opens the running one); the page loads it at start (`loadLive`), then again every
  minute and when the tab regains focus. Model names come from the ids in `modelUsage` (`pretty()`:
  `claude-opus-5-5` -> "Opus 5.5"), so the ambiguous `/stats` labels ("Opus 5" twice) don't appear.
  Without the server it falls back to the last file loaded in this browser (`cupstorm.models`), then
  `SAMPLE` (the /stats screenshot numbers, labels matched to model ids by token counts).
  "Load my usage" still parses `stats-cache.json`, session `.jsonl` logs, or `/stats` text copied with Ctrl+S.
- **Layout** (`build()`, `fillGlass()`): each model is a glass filled with cups, placed against the exact
  outline in `GLASS_POLY`; glasses are packed so labels and equations don't overlap.
- **Rendering**, three stacked canvases:
  - `#back` (2D): graph paper, see-through glass bodies, the All-glass water; redrawn only when the camera moves
    (`drawBack`).
  - `#glc` (WebGL2 instancing, WebGL1 + `ANGLE_instanced_arrays` fallback): every cup as one instanced quad;
    shaders `CUP_VS` / `STREAM_VS` do the tipping, pouring stream, draining, fading and per-cup blinking
    (sprite atlas: full | empty over eyes-closed) (`drawGL`). `WATER_FS` fills each model glass with translucent,
    rippling water (one instanced quad per glass) after the cups; `underWater()` in the cup and stream shaders
    discards every fragment the water covers, so cups behind the water vanish as through real water.
    Colours live in `WATER` (shared with the 2D sprites).
  - `#sky` (2D, takes input): glass rims, labels, "=" rows, the All glass (`frame`).
- **Blinking**: every face (cups, model glasses, All glass, burger/chocolate/roll) blinks ~0.14 s every 3-6 s
  on its own timer (`blinking()` on 2D, `uBlink` in `CUP_VS`); off with reduced motion.
- **Zoom stages**: each model glass pours while it shrinks on screen from `pourStart(cl)` (3 viewports tall, more
  for big glasses) to 0.6 (`pourOf`), so small glasses fill while you're zoomed in and big ones later. The
  level follows poured volume in the tapered glass (`levelV`). While a glass is pouring the wheel slows so a tick
  pours at most ~250 drawn cups (`wheelGain`). Per-model breakdown is a fixed eased move of `TRANSITION_S`
  (4.2 s), the same length as the pour into the All glass;
  past the per-model view, model glasses fly over and pour into the All glass (`morphAmount`, `pourPlan`).
  "All" locks that state until another view is chosen.
- **Counter** (top left): the big number is the cups on screen (`sceneInfo.onScreen` × `perCup`, or the exact
  total once every cup is in view); the line under it gives that water in litres, energy and, with Ground
  numbers on, burgers / chocolate bars / toilet rolls (`renderSub`).
- **Model chips** (bottom row) pop up only while that model's whole glass is on screen (`glassInView`), and hide
  during the All pour; clicking one flies to its glass.
- **Ground numbers** switch: shows burger / chocolate bar / toilet-roll equivalents (`EQUIV`).

Water equivalents: burger ≈ 2,400 L, 100 g chocolate bar ≈ 1,700 L, toilet roll ≈ 23 L (6 US gal).
