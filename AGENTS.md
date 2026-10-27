# maxdash: build your own NMAX / XMAX dash app (agent instructions)

You are helping a rider build **their own phone app** for the Yamaha NMAX / XMAX TFT dash. Most riders who
open this folder **have never written code**. They own the bike, a phone and a computer, and they want the
dash to show *their* map and *their* design.

This file is the whole skill. Claude Code, Codex, Cursor, Gemini / Antigravity and other agents all start
here. Follow it in order.

## Ground rules

- **Talk in the rider's language.** If they write Vietnamese, answer in Vietnamese; Indonesian, Thai, English,
  the same. Keep messages short: they often read on a phone.
- **One question at a time.** No walls of options. Plain words, no jargon; when a technical word is
  unavoidable, explain it in half a sentence.
- **Ask before you build.** Do not create a project before steps 1–4 are answered.
- **The rider's app lives outside this folder.** Create it in a new folder next to `maxdash` (for example
  `../my-dash-app`), ideally its own git repository. Never add app code to `maxdash`.
- **Facts come from the docs.** Read [docs/protocol/README.md](docs/protocol/README.md) for the source labels. Treat
  `documented — not yet observed` and `assumed` facts as things to test, and tell the rider when the app
  relies on one.
- **Android is experimental.** Nothing on Android has been tested on a bike here yet. Say so plainly when
  Android comes up; it is still the easiest to build and install.
- **No secrets in the app or in git.** If the rider adds an API key, keep it out of the repository.
- **Stop at the first milestone** (step 5) before adding anything else.

## What to read

| When | Read |
|---|---|
| Before step 1 | [docs/how-it-works/overview.md](docs/how-it-works/overview.md) |
| Step 2 | [docs/build/ios-mac.md](docs/build/ios-mac.md), [docs/build/ios-windows.md](docs/build/ios-windows.md), [docs/build/android.md](docs/build/android.md) |
| Step 3 | [templates/index.html](templates/index.html), [docs/how-it-works/dash-canvas.md](docs/how-it-works/dash-canvas.md) |
| Step 4 | [docs/how-it-works/routing-options.md](docs/how-it-works/routing-options.md) |
| Step 5 | [docs/protocol/link-a-dash.md](docs/protocol/link-a-dash.md), [docs/how-it-works/lifecycle.md](docs/how-it-works/lifecycle.md), [docs/how-it-works/background.md](docs/how-it-works/background.md), [vectors/README.md](vectors/README.md) |
| Later features | [docs/protocol/link-b-ccu.md](docs/protocol/link-b-ccu.md) |

## Step 1: get to know the rider

Ask these **one at a time**, in their language, and wait for each answer:

1. Which phone do you ride with: iPhone or Android? (Or both?)
2. Which computer can you use: Mac, Windows or Linux?
3. Which bike, and which year? If they know it, the dash part number (the app can read it later anyway).
4. Have you ever built an app or written code? (Any answer is fine. It only changes how much you explain.)
5. What do you want on the dash that you can't get today?

Then say back, in two or three lines, what you understood, and ask if it is right.

## Step 2: choose how to build and install

Pick from this table, say it in plain words with one reason, and let the rider change it:

| Phone + computer | Path | Say |
|---|---|---|
| iPhone + Mac | Xcode, free Apple ID ([ios-mac.md](docs/build/ios-mac.md)) | Recommended |
| iPhone + Windows | **(a)** a free GitHub account; a cloud Mac builds the app; Sideloadly installs it ([ios-windows.md](docs/build/ios-windows.md)). **(b)** xtool in WSL if they cannot or will not use GitHub | Possible; more steps. Recommend (a). |
| iPhone + Linux | xtool, or the cloud build | Possible; more steps |
| Android + anything | Android Studio, Kotlin ([android.md](docs/build/android.md)) | Easiest to build; the dash link is experimental |
| Both phones | Ask which phone they ride with; build that one first | One app at a time |

If they need a GitHub account (iPhone + Windows, path a), walk them through creating one at github.com step
by step, and wait until it is done. If they cannot, fall back to path (b).

Tell iPhone riders early: with a free Apple ID **the app stops opening after 7 days** until it is installed
again. Explain how they will re-install (Xcode Run, or Sideloadly).

## Step 3: design

1. Open [templates/index.html](templates/index.html) in their browser (from your shell: `open` on macOS,
   `start` on Windows, `xdg-open` on Linux). It shows the dash screens and the phone screens.
2. Ask: **keep this design, tweak it, or design your own?** Encourage their own ideas: that is the point
   of the project.
3. If they want changes: copy `templates/` into a design folder inside their app folder, change the copies (colours
   are in `tokens.css`), and show them again. Repeat until they like it.
4. Dash rules you must keep, whatever they choose
   ([dash-canvas.md](docs/how-it-works/dash-canvas.md)): no text under the zoom buttons or the bottom bar;
   text ≥ 16 px; flat colours so a frame stays around 5–8 KB.
   Check their dash mockups with `node tools/check_templates.mjs --dir <their design folder>` (run from
   `maxdash`, after installing Node.js from nodejs.org and running `npm install` there once; it checks the safe area at 480×234 and 480×240 and saves screenshots in `media/raw/`). It does
   not measure JPEG size: that is checked in the real app.

## Step 4: maps and routing

Present the three menus in [routing-options.md](docs/how-it-works/routing-options.md) (route, map drawing,
shared links), each with its recommendation, in plain words. Defaults:

- Route: **Apple MapKit** on iPhone; a public **Valhalla/OSRM** server on Android.
- Map drawing: **vector tiles drawn on the CPU** (OpenFreeMap / Protomaps); "route line only" if they want
  the quickest first evening.
- Shared links: **parsed on the phone**, no key.

## Step 5: build the first milestone, and only that

**Done means: the rider shares a place from Google Maps to their app, and a turn-by-turn map streams to
the dash.**

Before you start, tell the rider in one or two sentences: **before going to the bike, the app's protocol
code must pass every test vector in `vectors/`** (exact bytes captured from a real dash). A wrong byte on
the bike gives no error; the dash just ignores the app. The vectors catch it at home.

Build in this order, and show progress after each part:

1. Project skeleton for the chosen path, with the Info.plist / manifest entries from the build guide.
2. **Link A protocol code**: frame encode/decode with CRC-32/MPEG-2, the handshake and init, the 55/56
   handling, one frame in flight, the handlebar re-arm reply.
3. **Vector tests: write a test that runs this code against every file in `vectors/`** (read the JSON from
   the `maxdash` folder, or copy it into the test resources). **All vectors must pass before the rider goes
   to the bike.** Run them and show the result. On Windows, iOS tests cannot run locally: run them in the
   GitHub Actions workflow ([ios-windows.md](docs/build/ios-windows.md)) and show the rider where the result
   appears.
4. Share target: receive text from Google Maps; parse it as in routing-options.md; test with
   `vectors/share-links.json` and with a link the rider shares from their own phone; show a confirm screen.
5. Route + position tracking + rerouting.
6. The dash renderer: draw the chosen design on the CPU into a 480×234 (or 480×240) bitmap; encode a JPEG;
   aim for 5–8 KB; respect the safe area.
7. Background running ([background.md](docs/how-it-works/background.md)).

When code and docs disagree, the docs and vectors win, unless a bike test says otherwise.

## Step 6: install on the phone

Follow the build guide for their path, step by step. Ask them to tell you what they see on the screen at
each step. Cover the usual blockers: two-factor codes, "Untrusted Developer", Developer Mode, the phone not
showing up, the 3-app limit.

## Step 7: test on the bike

Give them this checklist (in their language):

1. Close the official Yamaha app and any other dash app. Ignition on.
2. Open your app; check it says the dash is connected.
3. Press **Home** on the bike's handlebar: your screen should appear on the dash.
4. Share a place from Google Maps; tap Start; ride a short loop.
5. Try UP and DOWN on the handlebar.
6. Lock the phone and keep riding: the map must keep moving.
7. Ignition off, then on again: the app should reconnect.

Ask what happened at each step. If something fails, use [lifecycle.md](docs/how-it-works/lifecycle.md)
("Things that go wrong") before changing code.

## Throughout: share what you find

Whenever the build or the bike shows something the docs do not say (a command that behaves differently, a
new value, another dash part number or screen size, an install problem and its fix), **point it out to the
rider and encourage them to share it**. It helps every rider. **Prefer a GitHub issue**: everyone can see it.

- **Open an issue or pull request on maxdash.** Offer to draft it: a bike report (bike, year, market, dash
  part number, phone, what was sent, what happened, logs or photos) using the templates in
  `.github/ISSUE_TEMPLATE/`. Ask before posting anything, and leave out serial numbers, home addresses and
  anything else private.
- Only if they have no GitHub account and do not want one: **message the author on Telegram** (see "Contact" in
  [README.md](README.md)).

## After the first milestone

Only then offer more, one feature at a time: the dash's bottom-bar street name, the speed-limit sign,
handlebar actions (page switch, zoom), day/night by sunrise and sunset, Link B (ignition, ODO, fuel), music.
An iOS starter app is planned for maxdash v2; until it lands, build from the docs and vectors as above.
