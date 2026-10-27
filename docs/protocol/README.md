# Protocol

How a phone app talks to the Yamaha NMAX / XMAX TFT dash and its connectivity unit.

> Compiled by the author from public information on the internet, then tested on the author's NMAX Turbo.
>
> Unofficial. Not affiliated with, endorsed by, or connected to Yamaha Motor or Garmin.

| File | What it covers |
|---|---|
| [link-a-dash.md](link-a-dash.md) | **Link A**: the dash. Frames, handshake, map frames, buttons, bottom bar, speed-limit sign, flow control |
| [link-b-ccu.md](link-b-ccu.md) | **Link B**: the connectivity control unit (CCU). Passkey, BLE, vehicle data, media, time, weather |
| [observations.md](observations.md) | Every bike test, in order: what was sent and what the bike did |
| [../../vectors/](../../vectors/README.md) | Test vectors: exact bytes your code must produce or accept |

## Source labels

Every fact in these files carries one label. Read the label before you rely on the fact.

| Label | Meaning |
|---|---|
| **observed** | Seen on a real bike. The label names the bike test in [observations.md](observations.md). |
| **partly observed** | Some of the behaviour was seen on a bike; the rest is still documented or assumed. The row says which part. |
| **documented — not yet observed** | From the author's compiled notes or public sources. Nobody has confirmed it on a bike yet. |
| **assumed** | Our interpretation or a design choice. Treat it as a guess. |

When a bike capture and a documented fact disagree, **the capture wins**, and the doc is updated.

## Tested so far

| Bike | Dash part | Screen | Phone | Links | First test |
|---|---|---|---|---|---|
| NMAX Turbo (Tech MAX) | `006-B3952-01` | 480×234 | iPhone 13, iOS 26.5 | A and B | 2026-10-24 |

Your bike is not in the table? Your report is the most useful thing you can send:
[open a bike report](../../CONTRIBUTING.md).
