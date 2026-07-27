# Capabilities, privacy, and threat model

## Xcode capabilities

* **HealthKit**: enable only for the optional Health feature; request only read types actually offered. HealthKit authorization status does not reveal whether read access was granted, so UI must not infer it.
* **App Groups / Keychain Sharing**: only if a reviewed extension/relay needs it. Use your provisioning identifiers; do not copy placeholder entitlements.
* Photos, Contacts, EventKit, and document picker do not use a generic filesystem entitlement. Sandbox restrictions remain in force.

Add the matching Info.plist keys in `Info.plist.snippet.xml`. Newer iOS versions use `NSCalendarsFullAccessUsageDescription` for full calendar access. Confirm requirements against the target iOS SDK and App Store policies before release.

## Threat model and controls

| Risk | Control |
|---|---|
| Over-collection | Separate per-domain consent, limited Photos picker, contacts field allowlist, calendar date window, selected Health types |
| Malicious MCP prompt | Gateway read-only tools, scope allowlist, data minimization, no tools that alter phone data |
| LAN attacker / stolen pairing | Mutual TLS, explicit two-device confirmation, Keychain keys with `WhenUnlockedThisDeviceOnly`, nonce/timestamp replay defense, certificate pinning where feasible |
| Lost device | Data Protection `completeFileProtection`, minimal retention, local deletion/revocation, no plaintext logs |
| Host compromise | Treat MCP host as privileged; explicit user disclosure, local-only sidecar default, audit transfer metadata, per-pair revocation |
| File-provider abuse | Security-scoped URLs, coordinated reads, copy into protected app storage, validate type/size, release security scope |
| Sensitive health data | Feature off by default; use HealthKit only after purpose-specific consent; do not infer denied read authorization |

Do not log contacts, event titles, file paths, media metadata, health samples, pairing secrets, or tokens. Obtain legal/privacy review, define retention, and provide export/delete controls before release.
