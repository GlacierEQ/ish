# Gateway protocol and export schema

## Boundary

The gateway accepts MCP-style JSON-RPC 2.0 messages, one UTF-8 JSON object per stdin line. It is **read-only**. A separate, future, authenticated iPhone-to-sidecar ingestion channel writes datasets; never let an MCP client issue device commands. Do not expose the process's standard I/O over a network endpoint.

Before an external transport is added, require a mutually authenticated TLS channel, pairing confirmation on both devices, a per-device key held in Keychain, replay protection, message-size limits, and an allowlisted localhost sidecar destination. Pairing secret configuration only makes an unconfigured gateway fail closed; this version does not validate the secret on stdin because stdio is presumed to be spawned by the trusted local MCP host.

## Methods

* `initialize` → advertised MCP capability metadata
* `tools/list` → `iphone_list_authorized_records`, `iphone_get_authorized_record`
* `tools/call` → invokes one tool
* `resources/list`, `resources/read` → `iphone://<authorized-kind>`

Tool calls return `-32001` for an ungranted scope. Unknown/invalid requests return JSON-RPC errors. Max request line: 1.1 MB; max data file: 10 MiB; maximum list limit: configured value, hard-capped at 500.

## Data contract

The trusted ingester writes one JSON array per kind: `photos.json`, `documents.json`, `contacts.json`, `calendar.json`, `health.json`, `imports.json`. Every object requires an opaque, stable `id`; include only approved, minimized fields. Suggested envelopes:

```json
{"id":"opaque-uuid","exportedAt":"2026-07-27T01:00:00Z","source":"photos","payload":{"createdAt":"…","filename":"…"},"consent":{"purpose":"user-selected export","approvedAt":"…"}}
```

Never place raw media, arbitrary document bytes, HealthKit values, credentials, or direct filesystem paths in default tool output. Store encrypted blobs separately and make any retrieval a distinct, consented design. `imports` is for user-selected call-history/voicemail exports, with `source`, file type, provenance, and import timestamp; it is not a claim that iOS supplied those records.

## Revocation / deletion

When consent is revoked, erase that kind's local dataset and derived indexes, invalidate the associated transport credential, and surface the deletion to the MCP client. Gateway scope changes require process restart. Keep audit events without sensitive record contents and retain only as long as disclosed.
