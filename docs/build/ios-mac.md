# iPhone + Mac (recommended for iPhone)

What you need: a Mac with the current Xcode (free from the App Store), an iPhone and its cable, and an Apple
ID. A free Apple ID works. The paid Apple Developer Program ($99/year) only changes two limits (below).

## One-time setup

1. Install Xcode and open it once to finish installing components.
2. Xcode › Settings › Accounts › **+** › Apple ID. Sign in. A "Personal Team" appears.
3. On the iPhone: Settings › Privacy & Security › **Developer Mode** › on (the phone restarts).

## Project settings your agent must set

| Setting | Value |
|---|---|
| Signing | Automatically manage signing, Team = your Personal Team |
| Bundle ID | unique to you, e.g. `com.<yourname>.mydash` (the share extension: `com.<yourname>.mydash.share`) |
| `UISupportedExternalAccessoryProtocols` | `com.garmin.navilite.data`, `com.yconnect.data` |
| `UIBackgroundModes` | `location`, `external-accessory`, `bluetooth-central` |
| Usage strings | `NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSBluetoothAlwaysUsageDescription` |
| Share extension | Accepts URLs and text; hands the text to the app through a custom URL scheme (App Groups may not be available on a free team). **Trap:** an extension cannot call `UIApplication.shared.open`, and the old `openURL:` trick no longer works on recent iOS. Walk the responder chain up to the `UIApplication` and call its modern open-with-options method; if that fails, keep the text and tell the rider to open the app. |

## Install

1. Plug the iPhone in, unlock it, tap **Trust**.
2. In Xcode pick the iPhone as the run destination and press **Run** (⌘R).
3. The first time, the iPhone refuses to open the app: Settings › General › VPN & Device Management ›
   your Apple ID › **Trust**.

## Free Apple ID limits

| Limit | Free | Paid |
|---|---|---|
| App expires | **after 7 days**: reconnect and press Run again (your data is kept) | after 1 year |
| Apps you can sideload at once | 3 per device | no limit |
| New App IDs | 10 per 7 days | no limit |

To avoid the 7-day surprise, rebuild every weekend, or automate it: `xcodebuild` + `xcrun devicectl device
install app` from a scheduled script while the phone is on the same Wi-Fi (pair it once for wireless
debugging in Xcode › Window › Devices).

## Troubleshooting

| Problem | Fix |
|---|---|
| "Untrusted Developer" when opening the app | Settings › General › VPN & Device Management › Trust |
| The iPhone does not appear in Xcode | Unlock it, re-plug, tap Trust; Developer Mode on; Xcode › Window › Devices and Simulators |
| Sign-in asks for a code | Two-factor authentication: enter the code shown on your other Apple device |
| "Maximum number of apps" | Delete another sideloaded app from the phone |
| The app runs but the dash never connects | The protocol strings are missing from Info.plist, or another app holds the dash (close the official app; cycle the ignition) |
