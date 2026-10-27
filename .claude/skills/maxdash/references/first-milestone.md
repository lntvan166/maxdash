# First milestone (AGENTS.md step 5)

Done = a place shared from Google Maps becomes a route, and a turn-by-turn map streams to the dash.

Order: skeleton → Link A protocol code → tests against every file in `vectors/` (all must pass before the
bike) → share target and link parsing (`vectors/share-links.json`) → route and rerouting → CPU dash renderer
(480×234/240 JPEG, 5–8 KB, safe area) → background running.

Docs: `docs/protocol/link-a-dash.md`, `docs/how-it-works/lifecycle.md`, `docs/how-it-works/background.md`,
`docs/how-it-works/routing-options.md`, `vectors/README.md`.
