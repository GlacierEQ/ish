# iPhone Companion + MCP Sidecar starter

A security-first starter for an iPhone app that **exports only data the person authorizes** and a local Python MCP gateway that exposes those exports to an MCP client. It is deliberately not an iPhone backup, filesystem browser, call-history reader, or voicemail reader.

## What is supported

| Data | iOS access model |
|---|---|
| Photos | Photo-library permission, then user-selected assets or limited-library access |
| Files | `UIDocumentPickerViewController`; security-scoped, user-selected files only |
| Contacts | `CNContactStore` authorization and selected fields |
| Calendar | `EKEventStore` authorization and bounded date query |
| Health (optional) | HealthKit authorization and explicitly selected sample types |
| Call history / visual voicemail | **No public unrestricted API**. Explicit user export/import workflow only |
| Arbitrary iPhone filesystem | **Not available**. Document-picker import only |

## Layout

* `swift/` — drop-in Xcode starter source; add to an iOS app target.
* `gateway/gateway.py` — dependency-free, line-delimited JSON-RPC/MCP gateway.
* `docs/` — protocol, privacy, threat-model, entitlement, and test notes.

## Quick gateway run

```sh
cd gateway
python3 gateway.py --data-dir ./data --config ./gateway-config.json
```

It communicates on stdin/stdout, one JSON-RPC object per line. Logs only go to stderr. Start with `gateway-config.example.json`, replace its pairing secret with a random value, and set restrictive scopes. The iOS app must deliver exported records to a separately implemented authenticated local transport; this starter intentionally does not open an unauthenticated LAN listener.

`gateway.py` implements `initialize`, `tools/list`, `tools/call`, `resources/list`, and `resources/read`. Its read-only tools return records previously written to `data/{photos,documents,contacts,calendar,health,imports}.json` by a trusted ingestion component. The included iOS transport is a pairing/client **stub**, not a production server.

## Xcode integration

1. Create an iOS 17+ SwiftUI app and add every file in `swift/` to its app target.
2. Add the usage descriptions in `docs/Info.plist.snippet.xml` to the target Info.plist (Health key only when HealthKit is enabled).
3. Enable the capabilities described in `docs/ENTITLEMENTS.md`; provision with an Apple Developer team.
4. Set a real app-group/keychain access-group only if sharing with extensions. Do not hard-code secrets.
5. Wire app UI buttons to the importers, render `AppModel.auditEntries`, and implement the transport server/relay after threat review.
6. Test on physical devices. Simulator results and compile checks are not permission/security validation.

## Explicit user-import workflows

For call history and voicemail, show a user-facing import screen explaining that iOS does not grant direct access. Let the person select a file they exported or manually created through `UIDocumentPickerViewController`; label provenance and import time, retain the original only if they choose, and send it through the same consent and encryption path. Never claim the app can scrape Phone or Visual Voicemail.

## Status and limits

Source is starter code, not a signed or device-tested application. No signing, entitlement provisioning, device permission testing, HealthKit review, or network transport deployment has been completed.
