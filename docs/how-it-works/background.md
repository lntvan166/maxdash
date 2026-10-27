# Running in a pocket

The phone is locked in a pocket while riding. Your app must keep routing, drawing and sending frames.

## iPhone

| Need | How | Source |
|---|---|---|
| Keep running | Background mode `location` with **Always** permission, and keep location updates on during a ride | observed (bike test 2026-10-24: streaming continued locked at the same rate) |
| Keep the dash link | Background mode `external-accessory` | observed (bike test 2026-10-24) |
| Link B | Background mode `bluetooth-central` | assumed (the Link B probe ran in the foreground) |
| Draw the map | **On the CPU** (Core Graphics into a bitmap, then a JPEG). No Metal, no MapKit views, no SwiftUI rendering while locked: iOS denies the GPU to background apps. | assumed (iOS rule; the CPU approach is what ran on the bike) |
| Speed | iPhone over this link: ~35–50 KB/s ≈ 4–5 fps at 7 KB per frame | observed (bike test 2026-10-24) |

`Info.plist` keys: `UIBackgroundModes` = `location`, `external-accessory`, `bluetooth-central`;
`UISupportedExternalAccessoryProtocols` = `com.garmin.navilite.data`, `com.yconnect.data`;
`NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationWhenInUseUsageDescription`,
`NSBluetoothAlwaysUsageDescription`.

## Android (experimental)

Nothing on Android has been tested on the author's bike yet. A public Android app (`pillion`) reports about
14 fps on an XMAX 2025 (480×234) over Bluetooth Classic, which would be much faster than the iPhone link.

| Need | How | Source |
|---|---|---|
| Transport | `BluetoothSocket` RFCOMM with the standard SPP UUID `00001101-0000-1000-8000-00805F9B34FB`, one writer thread, the same frames as iOS | documented — not yet observed |
| Keep running | A foreground service of type `connectedDevice` (plus `location` while navigating), and a battery-optimisation exemption | assumed |
| Wake on ignition | `CompanionDeviceManager` association with the bike's unit, so its presence starts the service | assumed |
| Permissions | `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN`, `ACCESS_FINE_LOCATION`, `ACCESS_BACKGROUND_LOCATION`, `POST_NOTIFICATIONS`, `FOREGROUND_SERVICE_CONNECTED_DEVICE`, `FOREGROUND_SERVICE_LOCATION` | assumed |
| Draw the map | `Bitmap` + `Canvas`, `Bitmap.compress(JPEG, …)` | assumed |
| Speed | Expected well above the iPhone's 4–5 fps (about 14 fps reported on an XMAX). The iPhone limits work as a start; measuring on your bike (Send→ACK, KB per frame, frames/s) is recommended but optional, and a report of the numbers is welcome | documented — not yet observed |

Open question: can the unit hold an Android phone on SPP while an iPhone keeps music (A2DP) at the same time?
If you test it, please send a report.
