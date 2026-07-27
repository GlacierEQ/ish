# Test checklist

- [ ] Build on the target iOS SDK with only enabled capabilities and required Info.plist strings.
- [ ] Test deny, limited, and allow flows for Photos; ensure only picker-selected/limited assets export.
- [ ] Test contacts/calendar denial, cancellation, and subsequent settings changes.
- [ ] Verify calendar date bounds and contact field allowlist; test empty stores.
- [ ] Test document cancellation, provider errors, oversized/type-rejected files, security-scoped URL lifecycle, and Data Protection after lock.
- [ ] Test HealthKit only on a physical device with selected sample types, including denial; do not interpret authorization status as read grant.
- [ ] Test explicit call/voicemail import: clear labeling/provenance, no claim of direct access, deletion path.
- [ ] Test pairing both-device confirmation, untrusted certificate, expired nonce, replay, key reset, revocation, and no plaintext secret logging.
- [ ] Run gateway malformed JSON, oversized line/data file, scope denial, invalid tool args, and dataset deletion tests.
- [ ] Conduct privacy/security review, accessibility/localization review, retention/deletion exercise, and real-device network test.
