# iPhone + Windows

Apple only ships its build tools for macOS, so this path has more steps. If you can borrow a Mac, use
[ios-mac.md](ios-mac.md). Otherwise pick one of the two paths below. Your agent will recommend (a).

| | (a) Cloud build + Sideloadly | (b) xtool in WSL |
|---|---|---|
| Builds on | a free macOS machine on GitHub | your PC |
| You install | Sideloadly, Apple's iTunes and iCloud for Windows | WSL, USBIPD, Swift, xtool, a ~10 GB Xcode download |
| Needs | a GitHub account | a fast disk and patience |
| Status | standard tools | **not yet tried with a dash app** (ExternalAccessory) |

## (a) Cloud build, then Sideloadly

1. Create a free GitHub account at github.com (your agent can walk you through it).
2. Install **GitHub Desktop** (desktop.github.com): the no-terminal way to send your code to GitHub.
3. Put your app's code in a repository of your own. A **public** repository gets free macOS build minutes;
   a private one gets a smaller free monthly allowance (macOS minutes count ten times), enough for a few
   builds a month.
4. Do not hand-write an Xcode project on Windows: describe it in a `project.yml` for
   [XcodeGen](https://github.com/yonaskolb/XcodeGen) and let the cloud Mac generate it. Put the protocol
   code and its vector tests in a target the workflow can test.
5. Add this workflow as `.github/workflows/build-ipa.yml` (adapt the names). It runs the vector tests first:
   their results show in the Actions log, and a red run means do not ride yet.

```yaml
name: build-ipa
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate the Xcode project
        run: brew install xcodegen && xcodegen generate
      - name: Vector tests
        run: |
          xcodebuild test -project MyDash.xcodeproj -scheme MyDashTests \
            -destination 'platform=iOS Simulator,name=iPhone 16' -quiet
      - name: Build unsigned app
        run: |
          xcodebuild -project MyDash.xcodeproj -scheme MyDash -configuration Release \
            -destination 'generic/platform=iOS' -derivedDataPath build \
            CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO build
      - name: Package .ipa
        run: |
          mkdir Payload
          cp -R build/Build/Products/Release-iphoneos/MyDash.app Payload/
          zip -qr MyDash.ipa Payload
      - uses: actions/upload-artifact@v4
        with:
          name: MyDash-ipa
          path: MyDash.ipa
```

6. Push (GitHub Desktop › Commit, then Push). On GitHub › Actions › the run › download the `MyDash-ipa` artifact and unzip it.
7. On Windows install **iTunes** and **iCloud** from apple.com (not the Microsoft Store versions), then
   **Sideloadly** from sideloadly.io.
8. Plug in the iPhone, open Sideloadly, drag in `MyDash.ipa`, enter your Apple ID, Start.
9. On the iPhone: Settings › General › VPN & Device Management › Trust; Settings › Privacy & Security ›
   Developer Mode › on.

Sideloadly signs the app (and its share extension) with your Apple ID. The same free-account limits apply
as on a Mac: **re-sign every 7 days** (Sideloadly can do it automatically while the PC is on), 3 apps per
device. Keep the protocol strings and background modes in the project's Info.plist: signing does not
remove them.

## (b) xtool in WSL

[xtool](https://github.com/xtool-org/xtool) is an open-source, cross-platform replacement for Xcode's
build-and-install steps. Facts checked on 2026-10-27:

| Item | Status |
|---|---|
| Hosts | Linux, WSL on Windows, macOS |
| Free Apple ID | Yes ("Password" login; it uses private Apple APIs, so a spare Apple ID is wise) |
| Needs | Swift 6.4 toolchain, `usbmuxd`, USBIPD on Windows to pass the iPhone into WSL, `Xcode.xip` downloaded from developer.apple.com (it extracts the iOS SDK) |
| Project | A Swift Package plus `xtool.yml`; `infoPath`, `entitlementsPath` and app extensions are supported |
| Dash app | **Not yet tried** with an ExternalAccessory app. If you try it, please send a report. |

Steps, in short (follow xtool's own "Installation (Linux/Windows)" guide for details):

1. Install WSL (Ubuntu) and USBIPD; bind the iPhone to WSL.
2. In WSL: install Swift 6.4 and `usbmuxd`; download the xtool AppImage into your `PATH`.
3. `xtool setup`: log in (Password mode), give it the path to `Xcode.xip`.
4. Your project needs an `xtool.yml` like:

```yaml
version: 1
bundleID: com.yourname.mydash
infoPath: Info.plist            # with UISupportedExternalAccessoryProtocols and UIBackgroundModes
extensions:
  - product: MyDashShare
    infoPath: Share/Info.plist
```

5. `xtool dev` builds, signs and installs on the plugged-in iPhone.

If you see `AFCClient.Error.muxError`, xtool's docs describe relaying the device through iTunes on Windows
instead of USBIPD.
