# Bike observations

Every test on a real bike, oldest first. Each **observed** label in the protocol docs and the vectors
points to one of these entries by its date. Add yours at the end (see [CONTRIBUTING.md](../../CONTRIBUTING.md)).

Format: `## <date> — <bike>, dash <part>, <reporter>`, then what was sent and what the bike did.

## 2026-10-24 — NMAX Turbo (Tech MAX), dash 006-B3952-01, author

Phone: iPhone 13, iOS 26.5.2, a free-signed test app. Accessory: `LinkCard`, `YAMAHA MOTOR Co.Ltd`,
fw 2.80, hw 3.00, protocols `com.garmin.navilite.data` and `com.yconnect.data`.

### Test 1: handshake and flow control

- Bike frames carry `01 03` at bytes 4–5 (`01 01` on cmd 55). The phone sends `01 06`. The CRC matched
  CRC-32/MPEG-2 on every bike frame.
- Handshake: bike 66 (serial `<serial>`) → phone 81 `01 00` + 33 `7C 06 00 01 00 00 00 00` → bike 82
  **before** 83 → bike 83 (XOR `0x0A`: part `006-B3952-01` + 4-byte key) → phone 84 key → bike 82 `01 00`.
- The init sequence (2, 31, 10, 14, 11, 13, 3, 17, 12) was sent on the first 82. The dash showed frames
  only after the rider pressed **Home**; the bike then sent 55 `01 00`.
- 56 arrived on ignition off and when the dash was overloaded. Bike speed arrived as 65 at 1 Hz.
  Handlebar DOWN arrived as 52.
- Map frames type `03`: the dash's own turn panel did not appear (cmd 2 `01` + 4 + 1 + 17 sent).
- Streaming continued with the phone locked, at the same rate.
- Window test (13.8 KB frames, 20 s each): window 1 → 3.1 fps / 314 ms; 2 → 3.7 / 539 ms; 3 → 3.6 / 812 ms
  with a loading spinner; no waiting → 0.3 fps, then the dash paused the stream (56).
- Size test (window 1, 15 s each): 20.7 KB → 2.1 fps / 466 ms; 15.0 KB → 2.6 / 376 ms; 9.9 KB → 3.7 / 256 ms;
  7.1 KB → 5.2 / 178 ms. Send→ACK ≈ 27 ms + 21 ms per KB.
- Later the same day, 13.8 KB frames took 179–214 ms instead of 300–420 ms. Conditions differed (engine,
  Link B up, dash page): re-measure before relying on constants.
- Link B was advertising over BLE (`YCCU_<ccu-code>`, RSSI −49 to −57 next to the bike) while Link A
  streamed. Both links run at the same time.

### Test 2: a real map

- The dash decoded a baseline JPEG (4:2:0, optimized Huffman, JFIF only). Night and day maps, a turn glyph,
  Vietnamese text and a drawn speed sign all displayed.
- 20–41 ms per KB this time (mostly 27–33). JPEG quality 0.30: 4.8–5.3 KB, 4.0–5.6 fps, visibly blocky.
  Quality 0.50: 7.0–7.8 KB, 3.8–4.6 fps. Quality 0.60: 7.5–8.5 KB, 4.0–4.4 fps. Both 0.50 and 0.60 looked fine.
- Thin saturated lines (a red ring, amber route edges) showed stair-stepped edges.
- The dash drew its own zoom buttons on the left and a dark road bar (`▲ Road`) at the bottom over the frame.
- Ignition off: 56, then the accessory disconnected.

### Calibration grid

A 480×234 grid with a 2 px line every 20 px. The whole frame is visible, edges included. The ＋ button is a
triangle pointing up (apex y ≈ 68, base y 99.5, x 9–49); the － button points down (base y 116, apex
y ≈ 147.5, x 9–49); both are opaque near-white with a dark glyph. The road bar runs from y 188 to the bottom,
full width, dark and semi-transparent. Photo: [calibration-grid.jpg](../how-it-works/assets/calibration-grid.jpg).

### Test 3: handlebar

- UP arrived as 51. In every session only the **first** press reached the phone. Replies tried after the
  first press, none of which re-armed the buttons: nothing; `51 []`; `20 []`; `2 [00]` + 14 + `13 [01 00]`;
  `13 [01 00]`; `51 [01 00]`.
- 4 fps with full map detail: 3.4–4.0 fps measured.

### Test 4: handlebar reply

- Replying **14 flag 1 `07 1A 00 00`** right after each 51/52 made every press arrive (UP, UP, DOWN, DOWN,
  2–4 s apart).
- A double press within 0.4 s was easy and reliable on the bike.

## 2026-10-25 — NMAX Turbo (Tech MAX), dash 006-B3952-01, author

Same bike and phone. Stationary, ignition on.

### Test 5: values, bottom bar, sign

| Step | Sent | What the dash did |
|---|---|---|
| 2-byte values | 2, 10, 11 as `00 00` | Map kept streaming; no visible change |
| Bottom bar | 3 flag 1, UTF-8 `Điện Biên Phủ`, then `Lê Lợi` | Bar shows `▲ Lê Lợi` with diacritics; `Road` is gone |
| Label and sign | 14 flag 1 `07 1A 05 00 "300 m"`; 17 flag 1 f32 50 + `km/h` | The dash drew its own sharp `50` sign at the right end of the bar; no `300 m` label |
| Resend after pause | 3, 10, 11 again on 55 after a 56 | Without the resend the bar went back to `Road`; with it, the road name showed again |

### Speed-limit sign

| Sent | Result |
|---|---|
| 17 flag 1, 50 / 60 + `km/h` | Red-ring sign 50 / 60, centre ≈ (442, 166), radius ≈ 31 px (covers ≈ x 411–473, y 135–197) |
| 17 flag 0, 0 | Sign stays: does **not** clear |
| 17 flag 1, 0 | Sign disappears |
| 14 flag 1 `07 1A len 00 "CAMERA 240 m"` | Nothing shown in plain-map mode |

### One app at a time

A second app on the same phone opened `com.garmin.navilite.data` in the background; the dash link dropped
until the ignition was cycled. With the official Y-Connect app installed, it woke up in the background
when the bike was in range, and opening `com.yconnect.data` at the same time made the unit drop.

### Link B: full chain

See [link-b-ccu.md](link-b-ccu.md) for the protocol. What the bike did:

- MFi `com.yconnect.data`: sent `01 00 00 00 02 01 39 04`, got `0x013A` (length 22): `01 3A` + 14-byte CCU
  code + 6-digit passkey.
- BLE: advertises `YCCU_<ccu-code>`. iOS may report it as already connected to the system. Max write 512.
- Nine characteristics on the service (see link-b-ccu.md). The two "indication" characteristics in the notes
  (`56DC2D58…`, `AB8D233A…`) are **not** on this unit; `1A1A7A79…` is there and not in the notes.
- ConnectAppId `00 02 seq 00 00 12 34` on `B606C7F9…`: no reply needed.
- DDT V1 send start on `56851826…`: **`[id, len24 BE]` (4 bytes)** works. The documented 5-byte
  `[01, id, len24]` was rejected (ATT error 13, invalid length). `[01, id, len16]` was accepted but never
  answered. The rest of the send went as documented.
- AuthenticationV2 accepted within ~0.1 s (`01 02 01` on `9C810D26…`).
- Sent unasked after auth: `00 01 02 15 00` (cmd 1), `01 21 02 50 01 "<serial>" 01` (289), `00 0B` (11,
  asks for language), `00 09` (9, asks for time), `01 29` (297).
- Ignition `01 37` → `01 38 01` (on) / `01 38 00` (off). Off is also pushed unasked, four times in ~1 s, then
  both links drop.
- ECU list `01 03`: the answer came over **DDT V1 receive**, not V2: request `[id, len24]` on `77808451…`,
  phone acks `[01, id]` on `1A1A7A79…`, data `[id, off24] + bytes` on `347456EE…`. Packet
  `01 04 00 00 03 18 E0 09` → ECU id 1248.
- Query 270 → 271 arrived over V2 (`E974B9A1…`). The first two bytes of the 4-byte notify header are a
  **counter**, not the command; the packet itself starts `01 0F len24`.
- Decoded: ODO raw `00 00 00 A3` = 163 → 16.3 km (the dash showed 16 km). Param 1 byte 6 `AA` → 12.45 V;
  byte 14 `46` → 40 °C coolant.
- Engine running ~40 s: battery 14.28–14.43 V, coolant 40 → 46 °C, fuel counter +101…+120 per 10 s
  (≈ 0.4 L/h). Param 1 bytes 0–1 went 0 → 1645 → 2120 → 3042 with the engine: probably RPM (assumed).
- Fuel `01 1F` → `01 20` + u32 LE counter; 0 while stationary.
- Time (9) and language (11) requests went unanswered with no visible effect within a minute.
