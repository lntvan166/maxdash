# Link A: the dash

The TFT dash shows a navigation screen that a phone app fills with **JPEG frames it draws itself**. The
phone also sets the dash's own bottom-bar text and speed-limit sign, and receives the handlebar buttons and
bike speed.

Read [README.md](README.md) for the source labels used below.

## Transport

| Phone | How the link is opened | Source |
|---|---|---|
| iPhone | ExternalAccessory, protocol string `com.garmin.navilite.data`. The accessory reports `name=LinkCard`, `mfr=YAMAHA MOTOR Co.Ltd`, and also offers `com.yconnect.data` (Link B). Declare both strings in `UISupportedExternalAccessoryProtocols`. A sideloaded app with a free Apple ID can open the session. | observed (bike test 2026-10-24) |
| Android | Bluetooth Classic RFCOMM to the dash's SPP service `00007220-0000-1000-8000-00805F9B34FB`: an insecure socket connected first try in ~0.45 s. Handshake, init and Home are the same bytes as on iPhone. The dash keeps several phones paired and talks to the one picked on its own device list. While the dash is set to another phone, it closes a dialled socket at once, before any byte. When it is switched to this phone on its device list, it opens the link itself to a listening `0x7220` server socket on the phone, and the session runs normally. Listen and dial at the same time. | observed (bike test 2026-10-31, Android 13) |
| Both | **Only one app at a time** can hold the dash link. If the official app or another dash app grabs it first, the unit may drop until the ignition is cycled. | observed (bike test 2026-10-25) |

The link stays up and keeps streaming at the same rate with the phone locked in a pocket (iOS: see
[background.md](../how-it-works/background.md)).

## Frame layout

Every message, both directions, is one frame:

| Offset | Size | Field | Notes | Source |
|---|---|---|---|---|
| 0 | 4 | Magic | `6E 41 6C 40` (ASCII `nAl@`) | observed (bike test 2026-10-24) |
| 4 | 1 | Version | `01` | observed (bike test 2026-10-24) |
| 5 | 1 | Direction | Phone sends `06`. Bike sends `03` (`01` on cmd 55). | observed (bike test 2026-10-24) |
| 6 | 1 | Command | See the tables below | observed (bike test 2026-10-24) |
| 7 | 4 | Payload length | u32 little-endian | observed (bike test 2026-10-24) |
| 11 | 1 | Flag | `0` = value, `1` = pointer/data. Some commands are **ignored** with the wrong flag (3, 14, 17). | observed (bike test 2026-10-25) |
| 12 | 4 | CRC | u32 little-endian, CRC-32/MPEG-2 over bytes 0–11 then the payload | observed (bike test 2026-10-24) |
| 16 | n | Payload | n = payload length | observed (bike test 2026-10-24) |

### CRC-32/MPEG-2

Polynomial `0x04C11DB7`, MSB first, init `0xFFFFFFFF`, no reflection, **no final XOR**. Check value for
ASCII `123456789` is `0x0376E6E7`. The CRC covers the 12 header bytes (without the CRC field) followed by
the payload.

```python
def crc32_mpeg2(data: bytes, crc: int = 0xFFFFFFFF) -> int:
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
    return crc

def frame(command: int, payload: bytes, flag: int = 0, direction: int = 0x06) -> bytes:
    head = b"nAl@" + bytes([0x01, direction, command]) + len(payload).to_bytes(4, "little") + bytes([flag])
    return head + crc32_mpeg2(head + payload).to_bytes(4, "little") + payload
```

### Reading frames

Bytes arrive in arbitrary chunks. Buffer them, scan for the magic, and drop anything before it. If a
length is absurd (say above 1 MiB), skip one byte and scan again. A frame whose CRC does not match is
best logged and ignored. (assumed: our robust-decoder choice, not a bike rule.)

## Commands: bike to phone

| Cmd | Payload | Meaning | Source |
|---|---|---|---|
| 66 | ASCII serial | First frame after the link opens. | observed (bike test 2026-10-24) |
| 82 | `01 00` | Authentication result. Arrives **before** 83 and again after the phone's 84. | observed (bike test 2026-10-24) |
| 83 | 12-byte part number + 4-byte key, every byte XOR `0x0A` | Challenge. The part number gives the screen size (below). | observed (bike test 2026-10-24) |
| 55 | `01 00` | Show frames: the rider pressed **Home** on the bike, or came back to the map. | observed (bike test 2026-10-24) |
| 55 | `03` / `04` | Open the favourites (3) or fuel (4) list. | documented — not yet observed |
| 56 | `03` / `04` | Close that list. | documented — not yet observed |
| 56 | other | Pause: the rider left the map screen, the ignition is going off, or the dash is overloaded. Stop sending frames. | observed (bike test 2026-10-24) |
| 65 | u16 LE at bytes 1–2 | Bike speed, 1 Hz. | observed (bike test 2026-10-24) |
| 65 | byte 0 = `01` | Value is in mph. | assumed |
| 51 | empty | Handlebar UP. | observed (bike test 2026-10-24) |
| 52 | empty | Handlebar DOWN. | observed (bike test 2026-10-24) |
| 80 | u16 LE | Frame ACK, carrying the sequence number the phone sent. The send-to-ACK timing below is observed; the payload encoding is not. | partly observed (bike test 2026-10-24) |
| 48 | index u16, listId u16, option u8 | Enter pressed on a list item. | documented — not yet observed |
| 49 | — | Stop the route. | documented — not yet observed |
| 53 / 54 | — | Go Home / go Work. | documented — not yet observed |

### Screen size from the part number

| Part number | Frame | Source |
|---|---|---|
| `006-B3952-01` | 480×234 | observed (bike test 2026-10-24) |
| contains `006-B4160` | 480×240 | documented — not yet observed |
| anything else | treat as 480×234, and please send a bike report | assumed |

## Commands: phone to bike

Values with flag 0 are **2 bytes**, `[value, 00]`, unless noted.

| Cmd | Flag | Payload | Meaning | Source |
|---|---|---|---|---|
| 81 | 0 | `01 00` | Hello, first reply to 66. | observed (bike test 2026-10-24) |
| 33 | 1 | `7C 06 00 01 00 00 00 00` | Hello, second part, right after 81. | observed (bike test 2026-10-24) |
| 84 | 1 | the 4-byte key from 83 (after XOR `0x0A`) | Challenge response. | observed (bike test 2026-10-24) |
| 2 | 0 | `00 00`, or `01 00` while navigating | Navigation state. 1-byte `00` also works. | partly observed (bike test 2026-10-25: 2-byte `00 00` keeps streaming; `01 00` untested) |
| 31 | 0 | `01 00` | Init. | observed (bike test 2026-10-24) |
| 10 | 0 | `01 00` / `00 00` | Home saved yes/no. No visible change in plain-map mode. | partly observed (bike test 2026-10-25) |
| 11 | 0 | `01 00` / `00 00` | Work saved yes/no. Same as 10. | partly observed (bike test 2026-10-25) |
| 13 | 0 | `01 00` | Init and show-frames reply. | observed (bike test 2026-10-24) |
| 14 | 1 | `07 1A len 00` + ASCII | Label. Sent with an **empty** text (`07 1A 00 00`) it re-arms the handlebar buttons. A non-empty text showed nothing in plain-map mode. | partly observed (bike test 2026-10-25) |
| 3 | 1 | UTF-8 text, ≤ 144 bytes, cut on a character boundary | **Bottom-bar text**, drawn as `▲ <text>`. Vietnamese diacritics display. With flag 0 the dash ignores it and keeps showing `Road`. A single space `20` clears it. | partly observed (bike test 2026-10-25: text and diacritics; ≤144 and the space rule are documented) |
| 17 | 1 | f32 LE limit, then u8 length, then `km/h` | **Speed-limit sign**: the dash draws its own red-ring sign at the right end of the bottom bar. Limit `0` with flag 1 removes it. Flag 0 does nothing (and does not clear). | observed (bike test 2026-10-25) |
| 12 | 0 | `01 00` | Last command of the init sequence. | documented — not yet observed |
| 16 | 0 | `[rtt ms / 100, 00]`, capped at 255 | Latency report after each ACK. | documented — not yet observed |
| 20 | 0 | empty | Pause ACK, reply to 56. | documented — not yet observed |
| 0 | 1 | see "Map frames" | A map frame. | observed (bike test 2026-10-24) |
| 4 | 1 | turnIcon u8, f32 distance, unitLen u8, roadLen u8, unit, road | The dash's own turn box (only in navigating mode 0). | documented — not yet observed |
| 1 | 1 | `[etaMin lo, hi, 00, 00]` | ETA for the dash's own turn box. | documented — not yet observed |
| 7 / 8 | 1 | `[n lo, n hi, 00]`, n ≤ 30 | Item count for list 3 / list 4. | documented — not yet observed |
| 98 / 99 | 1 | index u16, listId u16, octant u8 (0 none, 1–8 N…NW), nameLen u8 (≤ 128), unitLen u8, f32 distance, unit, name | One list item for list 3 / list 4. | documented — not yet observed |

## Handshake

| Step | Direction | Frame | Source |
|---|---|---|---|
| 1 | bike → phone | 66 serial | observed (bike test 2026-10-24) |
| 2 | phone → bike | 81 `01 00`, then 33 | observed (bike test 2026-10-24) |
| 3 | bike → phone | 82 `01 00` (early) | observed (bike test 2026-10-24) |
| 4 | bike → phone | 83 challenge | observed (bike test 2026-10-24) |
| 5 | phone → bike | 84 key | observed (bike test 2026-10-24) |
| 6 | bike → phone | 82 `01 00` (after 84) | observed (bike test 2026-10-24) |
| 7 | phone → bike | init sequence | partly observed (bike test 2026-10-24: sent on the early 82 and it worked; waiting for the 82 after 84 is documented) |

Robust rule: send the init once you have seen **83 and then an 82**. An 82 that arrives before 83 does not
count, and a repeated 83 resets it. If that never happens, send the init 2 s after the first 82.
(documented — not yet observed: the rule. The early-82 order itself is observed.)

### Init sequence

In this order, after the handshake:

| # | Cmd | Flag | Payload | Source |
|---|---|---|---|---|
| 1 | 2 | 0 | `00 00` | observed (bike test 2026-10-25) |
| 2 | 31 | 0 | `01 00` | observed (bike test 2026-10-24) |
| 3 | 10 | 0 | `00 00` (or `01 00` if Home is saved) | observed (bike test 2026-10-25) |
| 4 | 14 | 1 | `07 1A 00 00` | observed (bike test 2026-10-25) |
| 5 | 11 | 0 | `00 00` (or `01 00` if Work is saved) | observed (bike test 2026-10-25) |
| 6 | 13 | 0 | `01 00` | observed (bike test 2026-10-24) |
| 7 | 3 | 1 | bottom-bar text, or `20` | observed (bike test 2026-10-25) |
| 8 | 17 | 1 | limit `0` (no sign) | observed (bike test 2026-10-25) |
| 9 | 12 | 0 | `01 00` | documented — not yet observed |

### Showing frames

The dash shows the phone's frames only after the rider presses **Home** on the bike. The bike then sends 55
`01 00`. Reply with 2, 14, 13, then the current bottom-bar text (3) and the Home/Work flags (10, 11), then
start streaming. (observed (bike test 2026-10-25): the dash **forgets the bottom-bar text** across a
pause, so it must be resent on every 55.)

On 56 (pause), stop sending frames. Ignition off gives 56 and then the link closes.
(observed (bike test 2026-10-24))

## Map frames

| Field | Value | Source |
|---|---|---|
| Command / flag | 0 / 1 | observed (bike test 2026-10-24) |
| Byte 0: mode | `03` = plain map: the dash draws nothing of its own over the picture except its fixed chrome. `00` = navigating: the dash draws its own turn box from cmd 4 and 1. | partly observed (bike test 2026-10-24: mode 3; the turn box did not appear in mode 3, as expected) |
| Bytes 1–2 | frame id u16 LE, 1…65535 | documented — not yet observed |
| Bytes 3… | a baseline JPEG, 4:2:0, at the screen size (480×234 or 480×240) | observed (bike test 2026-10-24) |
| Small JPEGs | JPEGs ≤ 2048 bytes are zero-padded to 2050. Safer: never send one that small (re-encode at a higher quality). | documented — not yet observed |

What the dash accepts: a plain baseline JPEG with optimized Huffman tables and only a JFIF header decodes
fine. (observed (bike test 2026-10-24)) 4:2:0 halves colour resolution, so thin saturated lines (a red ring,
a thin amber edge) look stair-stepped: draw them thicker. (observed (bike test 2026-10-24))

The dash draws its own chrome **over** your picture. See [dash-canvas.md](../how-it-works/dash-canvas.md).

## Flow control and speed

**Send one frame, wait for its ACK (80), then send the next.** (observed (bike test 2026-10-24))

| Window (frames in flight) | Frames/s | Send→ACK | Dash |
|---|---|---|---|
| 1 | 3.1 | 314 ms | fine |
| 2 | 3.7 | 539 ms | fine |
| 3 | 3.6 | 812 ms | loading spinner |
| no waiting | 0.3 | 1415 ms | dash paused the stream (56) |

Frame size is the bottleneck. Send→ACK ≈ **27 ms + 21 ms per KB** (≈ 47 KB/s), and it varies from day
to day (20–41 ms/KB measured).

| JPEG size | Frames/s |
|---|---|
| 20.7 KB | 2.1 |
| 15.0 KB | 2.6 |
| 9.9 KB | 3.7 |
| 7.1 KB | 5.2 |

Targets: 6 fps needs ≤ ~6.5 KB per frame, 8 fps ≤ ~4.6 KB, 10 fps ≤ ~3.4 KB. A real map at JPEG quality
~0.5 came out at 7–8 KB and 4 fps looked good on the bike. **Design the dash map to compress**: flat
colours, few textures, no noise. (observed (bike test 2026-10-24))

When nothing changes on screen (stopped at a light), you can skip identical frames and send one every
2 s to keep the link alive. (assumed)

**The numbers above were measured on an iPhone.** On Android (bike test 2026-10-31, Android 13, synthetic JPEGs,
window 1, 25 frames per size) the dash took far more:

| Frame | Send→ACK median | fps | KB/s |
|---|---|---|---|
| 5 KB | 86 ms | 11.1 | 56 |
| 10 KB | 98 ms | 9.8 | 93 |
| 15 KB | 133 ms | 5.9 | 87 |
| 20 KB | 161 ms | 5.0 | 99 |

About twice the iPhone's rate, so the iPhone's limit is its own accessory path, not the dash. A window of 2 or 3
frames did not help. (observed (bike test 2026-10-31)) Measuring on your own phone is still recommended (optional);
a [bike report](../../CONTRIBUTING.md) with your numbers is welcome.

## Handlebar buttons

UP (51) and DOWN (52) reach the phone. **Right after each press, send 14 flag 1 `07 1A 00 00`**, or only
the first press of the session arrives. (observed (bike test 2026-10-24, test 4))

A double press (two within 0.4 s) is easy to do on the bike and useful as a second action.
(observed (bike test 2026-10-24, test 4)) The dash's own ＋/－ overlay stays visible whatever you send.

## Lists (favourites, fuel)

The dash has two list screens the phone can fill. On 55 `03` (favourites) or `04` (fuel): if navigating,
send 2 `00 00`; send the count (7 or 8), then each item (98 or 99). On 48 (Enter on an item) for a place:
start the route, send 2 `01 00`, then 4 and 1. On 56 `03`/`04`, restore 2 `01 00`.
(documented — not yet observed: this whole section)
