# Routing, map drawing and shared links

Your app needs three things the dash does not give you: a **route**, a **map picture** for each frame, and
a way to turn a **link shared from Google Maps** into a destination. None of them needs a server of your
own. Each has a recommended default.

## Route: from here to there

| Option | Cost | Traffic | Notes |
|---|---|---|---|
| Apple MapKit directions (iOS) | Free | Some | **Recommended on iPhone.** Built into iOS (`MKDirections`), no key. Car or walking profiles only; fine for a scooter in town. |
| Public OSRM / Valhalla demo servers | Free | No | Fair-use limits; may be slow or down. Valhalla has a `motor_scooter` profile. Good default on Android. |
| Your own Google Routes API key | Pay as you go, with a free monthly tier | Yes | Best routes and live traffic, two-wheeler mode in some countries. Fine for a personal build; **never ship the key inside an app you share** with others. |
| Self-hosted Valhalla | Free, needs an always-on machine | No | For people who already run a home server. |

How to choose:

- **iPhone:** start with MapKit. Switch to a Google key later if you want traffic.
- **Android (experimental):** start with a public Valhalla or OSRM server. A Google key is the upgrade.
- **Both phones:** use the same option on both so routes match: public Valhalla/OSRM, or a Google key.

Rerouting: when the rider leaves the route by more than ~40 m for a few seconds, ask for a new route from
the current position. Throttle it (at most one request every ~10 s).

## Map drawing: what becomes the JPEG

The dash shows a JPEG your app draws. On iPhone the phone is usually locked in a pocket, so drawing must
work **in the background on the CPU**: no GPU, no MapKit views (see [background.md](background.md)).

| Option | Cost | Works when locked | Notes |
|---|---|---|---|
| Vector tiles from OpenFreeMap or Protomaps, drawn on the CPU | Free | Yes | **Recommended.** Download the tiles around the route when the ride starts and cache them. Draw roads, water and parks as flat shapes; it compresses well. |
| Route line only, no base map | Free | Yes | Simplest. Draw the route and the roads it uses from the route geometry. A good first evening. |
| `MKMapSnapshotter` (iOS) | Free | Unreliable | Only for a preview in the app while it is open. |
| Google Static Maps | Needs a key | Yes | A network request per frame, slow and costly. Not recommended. |
| `tile.openstreetmap.org` raster tiles | — | — | **Do not use.** The [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/) forbids this kind of use. |

Keep each frame at about 5–8 KB (see [flow control](../protocol/link-a-dash.md#flow-control-and-speed)) and
inside the [safe area](dash-canvas.md#safe-area).

## Shared links: Google Maps → destination

The rider finds a place in Google Maps and taps **Share**, then your app. Your app receives text or a URL.
Turn it into a destination **on the phone, with no key**:

1. Find the first `http(s)://` URL in the shared text. Google Maps shares a name, address lines, then a
   short link.
2. If it is a short link (`maps.app.goo.gl`, `goo.gl/maps`), request it **without following redirects**,
   read the `Location` header, and parse that URL instead. If that URL is itself a redirector, repeat (up to
   about 5 hops).
3. Parse, in this order:

| Link shape | Take |
|---|---|
| `…/maps/dir/<origin>/<stop>/…/<destination>/…` | The last segment is the destination, the ones between are stops (the first is the origin). Coordinates are `!1d<lng>!2d<lat>` per waypoint in the `data=` part, in order. A waypoint without coordinates: search its text. |
| `…/maps/place/<name>/…!3d<lat>!4d<lng>` | `!3d`/`!4d` (the place), **not** the `@lat,lng` viewport |
| `?q=<lat>,<lng>`, `?ll=<lat>,<lng>`, `query=<lat>,<lng>`, `destination=<lat>,<lng>` | Those coordinates |
| `@<lat>,<lng>,<zoom>z` only | The viewport centre |
| Text instead of coordinates in `?q=`, `query=`, `destination=`, `daddr=` (short place links often resolve to `?q=<Name, Address>&ftid=…`) | Search that text (next row) |
| A name only (`/maps/place/<name>/`, `query=<text>`) | Search the name: MapKit `MKLocalSearch` on iPhone, or public Photon / Nominatim (fair use). Show the top result and **let the rider confirm**. |
| Coordinates out of range, not a maps link | Say so; do not guess |

4. Optional upgrade: a Google Places key resolves names better than free search.

This parsing is fragile: Google changes link shapes without notice. Test it with
[share-links.json](../../vectors/share-links.json) and with links you share from your own phone.
