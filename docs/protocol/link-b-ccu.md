# Link B: the CCU

> **Status: mostly untested. Reports wanted.** Authentication and vehicle data (ignition, ODO, battery,
> coolant, fuel) were seen on one bike. Media, time, language, battery report and weather are documented
> only. If you try any of them, please [send a bike report](../../CONTRIBUTING.md).

The communication control unit (CCU) is the bike's second link. The official app uses it for music, calls,
weather, time and vehicle data. You do **not** need it to stream a map to the dash (that is
[Link A](link-a-dash.md)). Both links run at the same time. (observed (bike test 2026-10-24))

Read [README.md](README.md) for the source labels.

## Overview

1. Over MFi (`com.yconnect.data`), ask for the CCU code and a 6-digit passkey.
2. Connect over BLE to `YCCU_<code>`, enable notifications, authenticate with code + passkey.
3. Exchange commands: short ones as single writes, long ones through a chunked channel ("DDT").

On Android the first step uses Bluetooth Classic instead of MFi. (assumed)

## Step 1: code and passkey (MFi)

Open an ExternalAccessory session on `com.yconnect.data`. Frames on this stream:

| Field | Size | Value |
|---|---|---|
| SOH | 1 | `01` |
| length | 4 | u32 big-endian, = 2 + body length |
| cmd | 2 | u16 big-endian |
| body | length − 2 | |
| EOT | 1 | `04` |

| Step | Bytes | Source |
|---|---|---|
| Ask (cmd `0x0139`) | send exactly `01 00 00 00 02 01 39 04` | observed (bike test 2026-10-25) |
| Answer (cmd `0x013A`) | read frames until one has length 22 and cmd `01 3A`: payload bytes 2–15 = CCU code (14 ASCII), 16–21 = passkey (6 ASCII digits) | observed (bike test 2026-10-25) |
| Keep it open | do **not** close this session while you connect and authenticate over BLE; keep reading and discarding bytes | documented — not yet observed |

If the official app is installed it may hold this session; the unit then drops. Ask the rider to close
it. (observed (bike test 2026-10-25))

## Step 2: BLE

| Item | Value | Source |
|---|---|---|
| Name | `YCCU_<code>` | observed (bike test 2026-10-25) |
| Already connected | iOS may report the CCU as already connected to the system: retrieve connected peripherals for the service instead of scanning | observed (bike test 2026-10-25) |
| Service | `AFA2CDF4-ECCF-46A7-A5EA-9DA428C0157A` | observed (bike test 2026-10-24) |
| MTU | ask 512; iOS reported a max write of 512. Chunk size = clamp(mtu − 7, 20, 180) | partly observed (bike test 2026-10-25: 512; the chunk rule is documented) |

### Characteristics

| UUID | Props | Role | Source |
|---|---|---|---|
| `B606C7F9-E5A1-4E75-B313-2A920054A8EB` | write | CMD write: short commands `[cmd hi, cmd lo, payload…]` | observed (bike test 2026-10-25) |
| `9C810D26-B605-4306-8C1C-755A1BA3066C` | notify | CMD notify: short commands from the bike | observed (bike test 2026-10-25) |
| `75AB2788-87F6-4F61-BA9C-6F85A12600D1` | read, notify | DDT V1 send: handshake | observed (bike test 2026-10-25) |
| `56851826-A090-4F6A-A5DF-D1776520F74A` | write | DDT V1 send: start / close | observed (bike test 2026-10-25) |
| `E998AEAB-EA8F-4063-83AA-2017C1A44484` | write | DDT V1 send: chunks | observed (bike test 2026-10-25) |
| `77808451-E42F-4F6B-83ED-3AB44AA3D16A` | notify | DDT V1 receive: the bike announces a packet | observed (bike test 2026-10-25) |
| `1A1A7A79-…` | write | DDT V1 receive: the phone's ack | observed (bike test 2026-10-25) |
| `347456EE-A588-4DD5-BD98-62BE3672E27A` | read, notify | DDT V1 receive: chunks | observed (bike test 2026-10-25) |
| `E974B9A1-FA31-43C6-91AE-09931F3F6EF1` | notify | DDT V2 receive (vehicle data) | observed (bike test 2026-10-25) |
| `56DC2D58-CBE1-4BA9-A104-E9B8EB4DA95C`, `AB8D233A-CC58-4932-B397-A3751911E021` | indicate | in the notes; **not present** on the tested unit | documented — not yet observed |

The full `1A1A7A79` UUID is printed by iOS on discovery; match it by prefix. (assumed)

Enable notifications **one characteristic at a time**: write the CCCD (`00002902-…`), wait for the callback,
then the next. (documented — not yet observed: the one-at-a-time rule)

## Step 3: authenticate

| # | Do | Source |
|---|---|---|
| 1 | Write ConnectAppId to CMD write: `00 02 <seq> 00 00 12 34`. No reply. | observed (bike test 2026-10-25) |
| 2 | Send AuthenticationV2 through **DDT V1 send**: 22 bytes, `01 01` + CCU code (14 ASCII) + passkey (6 ASCII) | observed (bike test 2026-10-25) |
| 3 | Wait for `01 02 01` on CMD notify (cmd 258, byte 2 = 1: accepted). Came in ~0.1 s. | observed (bike test 2026-10-25) |
| 4 | From now on answer every ping 309 `01 35 <token>` with 310 `01 36 <token>` on CMD write | documented — not yet observed |

Sent unasked right after auth: cmd 1 `00 01 02 15 00`, 289 `01 21 …` (carries the bike serial), 11
`00 0B` (asks for the language), 9 `00 09` (asks for the time), 297 `01 29`. The meaning of 1, 289's other
bytes and 297 is unknown. (observed (bike test 2026-10-25))

## DDT: long packets

### Phone → bike (DDT V1 send)

| Step | Do | Source |
|---|---|---|
| A | Pick `id` 1…255 (rotate, skip 0). Read `75AB2788`. | observed (bike test 2026-10-25) |
| B | When the read completes, write the start to `56851826`: **`[id, len >> 16, len >> 8, len]`** (4 bytes) | observed (bike test 2026-10-25: the 5-byte form `[01, id, len24]` in older notes is rejected with ATT error 13) |
| C | Wait for notify `[01, id]` on `75AB2788` | observed (bike test 2026-10-25) |
| D | For each chunk at `offset`: write `[id, off >> 16, off >> 8, off] + chunk` to `E998AEAB`, one after another | observed (bike test 2026-10-25) |
| E | After the last write completes: write `00 00` to `56851826`, wait for notify `00 00` on `75AB2788`, then 80 ms before the next packet | partly observed (bike test 2026-10-25: the close; the 80 ms gap is documented) |

### Bike → phone (DDT V1 receive)

Used for the ECU list answer. (observed (bike test 2026-10-25))

1. The bike notifies `[id, len24]` on `77808451`.
2. The phone acks with `[01, id]` on `1A1A7A79`.
3. Chunks arrive as `[id, off24] + bytes` on `347456EE`. Reassemble by offset until `len` bytes.

### Bike → phone (DDT V2 receive)

Used for vehicle data. Each notify on `E974B9A1` is `[c0, c1, fragIndex, lastFragIndex] + bytes`. Start a
new buffer at fragIndex 0; the packet is complete at fragIndex ≥ lastFragIndex.
(partly observed (bike test 2026-10-25): **c0 c1 is a counter**, not the command as older notes say. The
reassembled packet starts with its own `cmd hi, cmd lo, len24`.)

## Vehicle data

| What | Ask | Answer | Decode | Source |
|---|---|---|---|---|
| Ignition | `01 37` (311) on CMD write | `01 38 <s>` (312) | 1 on, 0 off. Off is also pushed unasked (several times), then both links drop. | observed (bike test 2026-10-25) |
| ECU list | `01 03` (259) on CMD write | 260 via DDT V1 receive | skip 5 bytes (`01 04 len24`), then protobuf field 3 (varint or packed) = ECU ids. Tested unit: `18 E0 09` → 1248. | observed (bike test 2026-10-25) |
| ODO, battery, coolant | 270 via DDT V1 send: `01 0E len24` + protobuf `18 <ecu varint> 22 02 01 48` | 271 via DDT V2 receive | skip 5 bytes; each field 4 block = {field 1 paramId, field 2 raw}. Param 72: raw big-endian ÷ 10 = km. Param 1 (≥ 16 bytes, byte 6 ≠ 0): byte 6 × 18.75 / 256 = volts; byte 14 − 30 = °C. | observed (bike test 2026-10-25) |
| Engine RPM | (in param 1) | | bytes 0–1 u16 BE: 0 engine off, 1645–3042 while idling and blipping | assumed |
| Fuel used | `01 1F` (287) on CMD write | `01 20` + u32 LE counter (288) | litres = Δcounter / 100 000; ignore a jump ≥ 2 L | partly observed (bike test 2026-10-25: counter and rate plausible; litres scale documented) |

Ask every 10 s. (documented — not yet observed: the period)

## Phone → bike: time, language, phone status

| What | Write to CMD write | When | Source |
|---|---|---|---|
| Time (cmd 10) | `00 0A <seq>` + 8 bytes BE of local epoch seconds (UTC seconds + time-zone offset) | after auth, and when the bike asks with 9 | observed (bike test 2026-10-31): the dash clock matched the phone |
| Language (cmd 12) | `00 0C <seq> <lang>`: 15 Vietnamese, 0 English | after auth, and when the bike asks with 11 | documented — not yet observed |
| Phone status (cmd 316) | `01 3C <battery> <callVol> <mediaVol> <flags>`. Each percentage byte = (0…100 & 0x7F) \| 0x80 when valid. flags = 1 \| btAudio << 1 \| (thermal 0–2) << 2 \| (signal bars 0–5) << 4 | on change | observed (bike test 2026-10-31): the dash's battery and signal icons matched the phone |

## Media and calls

| Bike → phone | Meaning | Phone reply | Source |
|---|---|---|---|
| 279 (`01 17`) | media key, byte 2: 1 next, 2 previous, 3 play, 4 pause | act, then send track info (278) | documented — not yet observed |
| 281 (`01 19`) | call key, byte 2: 0 reject, 1 answer, 2 end | 308 `01 34 [1]` in call / `[2]` ended (iOS apps cannot control calls) | documented — not yet observed |
| — (phone call starts / ends) | none: the phone sends 308 unasked | `[1]` shows a steady call icon (it does not blink), `[2]` clears it | observed (bike test 2026-10-31) |
| 285 (`01 1D`) | volume / mute, byte 2: 1/2 media ±, 3/4 call ±, 5 media mute, 6 mic mute | 316 phone status | documented — not yet observed |

### Track info (278, via DDT V1 send)

`01 16`, then artist, album and title, each as `[len u8] + UTF-8` (cut to ≤ 64 bytes on a character
boundary), then duration seconds (u24 BE), play state (1 paused, 2 playing, 3 forward, 4 rewind, 255
stopped), speed in tenths (u16 BE, 10 = 1.0×), position seconds (u24 BE).
(documented — not yet observed)

## Weather

When the bike sends cmd 3 with ≥ 11 bytes and byte 2 = 0, bytes 3–6 and 7–10 are latitude and longitude as
int32 BE radians × 10⁸. Reply with cmd 4 (area name) and ten cmd 5 frames (forecast).
(documented — not yet observed: this whole section)

| Reply | Bytes |
|---|---|
| Area (4) | `00 04 <seq>` + UTF-8 place name, ≤ 21 bytes |
| Forecast slot (5) | `00 05 <seq> <slot> <icon> <temp i16 BE> <max i16 BE> <min i16 BE> <precip ÷ 5>`; temperatures × 10 (31.5 °C → `01 3B`); precip 0–100 % → 0–20 |

Slots: 0 now; 1–5 and 9 the next six days (temp = (max + min) / 2); 6–8 the next three hours (max = min = 0).

Icon codes from WMO weather codes (day / night):

| WMO | Icon |
|---|---|
| 0 clear | 0 / 128 |
| 1, 2 partly cloudy | 1 / 129 |
| 3 overcast | 2 / 130 |
| 45, 48 fog | 8 |
| 51, 53, 55, 61 light rain | 16 |
| 56, 57 freezing drizzle | 20 |
| 63 rain | 3 |
| 65, 82 heavy rain | 17 |
| 66, 67 freezing rain | 7 |
| 71–77, 85, 86 snow | 4, 18, 19 |
| 80, 81 showers | 13 / 141 |
| 95 thunderstorm | 14 / 142 |
| 96, 99 thunderstorm with hail | 12 |
| anything else | 15 |
