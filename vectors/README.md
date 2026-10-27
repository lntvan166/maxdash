# Test vectors

Exact bytes your app must produce or accept, in the format seen on a real dash. They are plain JSON, so any
language can use them.

**Rule: your code must pass every vector before you ride.** A wrong byte on the bike gives no error
message: the dash simply ignores you. A failing vector on your computer tells you which byte is wrong.

| File | What your test does |
|---|---|
| [crc.json](crc.json) | Run your CRC-32/MPEG-2 over `input.hex`; compare with `expect.crc32_mpeg2` |
| [frames.json](frames.json) | Encode a phone→bike frame from `input`; compare byte for byte with `expect.frame_hex` |
| [link-a-commands.json](link-a-commands.json) | Decode a bike→phone `input.frame_hex`; check magic, length and CRC; compare command, flag, payload, and what it `means` |
| [handshake-nmax-turbo.json](handshake-nmax-turbo.json) | Feed the bike frames to your session logic in order; after each, your app must have sent exactly `must_send`, in order |
| [share-links.json](share-links.json) | Parse text shared from Google Maps into a destination (see [routing-options.md](../docs/how-it-works/routing-options.md)) |

## Format

```json
{
  "schema": 1,
  "about": "what the file tests",
  "vectors": [
    {
      "id": "hello-81",
      "label": "observed",
      "source": "observations.md#2026-10-24",
      "note": "Hello, first reply to 66",
      "input": { "direction": 6, "command": 81, "flag": 0, "payload_hex": "01 00" },
      "expect": { "frame_hex": "6E 41 6C 40 01 06 51 02 00 00 00 00 1A 4D 1C EC 01 00" }
    }
  ]
}
```

- Hex strings are upper case, space separated.
- `label` uses the same three labels as the docs: `observed`, `documented — not yet observed`, `assumed`.
  An `observed` vector names the bike test in [observations.md](../docs/protocol/observations.md).
- A vector that combines several facts (the handshake session) carries the **weakest** label among them;
  `check_vectors.py` enforces it.
- Some bike→phone vectors are built in the observed format with example values (a speed of 40 km/h, a
  placeholder serial) rather than copied from a capture; their `note` says so.
- Private values from the test bike (its serial) are replaced with placeholders; the CRCs are computed
  for the placeholder.

## Checking the vectors themselves

```sh
python3 tools/check_vectors.py
```

It recomputes every CRC and frame with its own implementation and checks labels and sources. Run it
after editing a vector.

## Adding vectors

Saw a new frame on your bike? Add it here with `"label": "observed"`, add your test to
[observations.md](../docs/protocol/observations.md), and open a pull request (see
[CONTRIBUTING.md](../CONTRIBUTING.md)).
