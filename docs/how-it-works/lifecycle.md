# Lifecycle: from ignition on to ignition off

| # | Bike | Phone app | Source |
|---|---|---|---|
| 1 | Ignition on; the unit powers up | iPhone: the accessory appears (`EAAccessoryDidConnect`). Android: connect the SPP socket. Open the session. | observed (bike test 2026-10-24) |
| 2 | Sends 66 (serial) | Replies 81 `01 00`, then 33 | observed (bike test 2026-10-24) |
| 3 | Sends 82, then 83 (challenge) | Replies 84 with the key; reads the screen size from the part number | observed (bike test 2026-10-24) |
| 4 | Sends 82 `01 00` | Sends the init sequence | observed (bike test 2026-10-24) |
| 5 | Waits for the rider | Nothing on the dash yet. Keep the route and drawing ready. | observed (bike test 2026-10-24) |
| 6 | Rider presses **Home**; bike sends 55 `01 00` | Resends state (2, 14, 13, 3, 10, 11) and starts streaming | observed (bike test 2026-10-25) |
| 7 | ACKs each frame (80); sends speed (65) at 1 Hz; buttons 51/52 | One frame in flight; reply 14 `07 1A 00 00` after every button | observed (bike test 2026-10-24) |
| 8 | Rider leaves the map, or overload: 56 | Stop frames (reply 20, documented). On the next 55, go back to step 6. | observed (bike test 2026-10-24) |
| 9 | Ignition off: 56, then the link closes | Clean up; wait for the next connect | observed (bike test 2026-10-24) |

Exact bytes: [link-a-dash.md](../protocol/link-a-dash.md) and the [handshake vector](../../vectors/handshake-nmax-turbo.json).

## Things that go wrong

| Symptom | Likely cause |
|---|---|
| The accessory never shows up (iPhone) | The protocol string is missing from `UISupportedExternalAccessoryProtocols`, or another app holds the link. Close the official app and other dash apps; cycle the ignition. |
| Handshake done but the dash shows nothing | The rider has not pressed Home, or frames are sent before 55. |
| Only the first button press arrives | Missing the 14 `07 1A 00 00` reply after each press. |
| Spinner on the dash | More than one frame in flight, or frames too big. |
| Bottom bar says `Road` after a pause | Bottom-bar text (3) not resent on 55. |
| Street name ignored | Cmd 3 sent with flag 0; it needs flag 1. |
