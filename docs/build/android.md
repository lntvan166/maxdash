# Android

> **Experimental.** Nothing on Android has been tested on the author's bike yet. The dash link on Android
> (Bluetooth Classic SPP) is documented and a public Android app reports it working on an XMAX, but your
> report would be the first here. Building and installing is the easy part.

What you need: Windows, macOS or Linux; [Android Studio](https://developer.android.com/studio) (free); an
Android phone (Android 10 or newer) and its cable. No account or fee.

## One-time setup

1. Install Android Studio; let it download the SDK.
2. On the phone: Settings › About phone › tap **Build number** 7 times (Developer options appear), then
   Settings › Developer options › **USB debugging** on.
3. Plug the phone in and accept the "Allow USB debugging" prompt.

## Project settings your agent must set

| Setting | Value |
|---|---|
| Language | Kotlin |
| minSdk | 29 (Android 10) |
| Dash link | `BluetoothSocket` RFCOMM, SPP UUID `00001101-0000-1000-8000-00805F9B34FB`, to the bike's unit (pair it first in the phone's Bluetooth settings) |
| Background | A foreground service (types `connectedDevice` and `location`) with a visible notification during a ride |
| Permissions | `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN`, `ACCESS_FINE_LOCATION`, `ACCESS_BACKGROUND_LOCATION`, `POST_NOTIFICATIONS`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_CONNECTED_DEVICE`, `FOREGROUND_SERVICE_LOCATION` |
| Share target | An activity with an `ACTION_SEND` intent filter for `text/plain` (Google Maps shares text) |
| Battery | Ask the rider to exempt the app from battery optimisation |

## Install

Press **Run** in Android Studio with the phone selected. The app stays installed; there is no expiry.
To give the app to a friend, build an APK (Build › Build APK) and send it; they allow "Install unknown
apps" for the file manager they open it with.

## Troubleshooting

| Problem | Fix |
|---|---|
| The phone does not show up | Another cable (some are charge-only); accept the USB debugging prompt |
| Socket connect fails | Pair the bike's unit in Bluetooth settings first; only one app may hold the link; cycle the ignition |
| Stops when the screen is off | Foreground service missing, or battery optimisation still on |

Please send a bike report with what worked: see [CONTRIBUTING.md](../../CONTRIBUTING.md).
