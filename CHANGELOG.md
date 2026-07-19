# Changelog

## 0.3.4 — 2026-07-17

### Security
- **Relay SSRF guard now checks resolved DNS addresses, not just IP
  literals.** `validate_relay_url` previously only blocked hostnames that
  literally parsed as private/loopback/link-local/reserved IPs, so a DNS
  name resolving to an internal address (e.g. `169.254.169.254` cloud
  metadata, `127.0.0.1`) bypassed the guard entirely. Hostnames are now
  resolved via `getaddrinfo` and EVERY resolved address is checked against
  the block list (loopback, private, link-local, reserved, multicast,
  unspecified — with IPv4-mapped IPv6 unwrapped). Unresolvable hostnames
  fail closed with `ValueError`. IPv6 unspecified (`[::]`) literals are now
  also rejected. Note: validation resolves at check time; full DNS-rebinding
  protection would additionally require pinning the vetted IP for the dial.

## 0.3.3 — 2026-07-17

### Fixed
- **NIP-46 bunker `connect()` sent the wrong params.** It sent the client's own
  pubkey and dropped the bunker URL's `secret` query parameter. It now sends
  `[remote-signer-pubkey, secret]` per NIP-46, reads the signer's response,
  and raises `RuntimeError` if the signer rejects the connection.
- **npub-form bunker URLs never worked.** `bunker://npub1...` URLs stored the
  npub raw, so the relay `authors` filter, the `p` tag, and the response
  pubkey check (all hex-based) matched nothing and the client hung forever.
  The remote signer pubkey is now normalized to hex on connect and validated;
  malformed netlocs raise `ValueError`. Hex-form URLs are unchanged.
- **Bunker requests can no longer hang forever.** `connect()` and all NIP-46
  requests now time out (default 60s, tunable via `connect(..., timeout=)`)
  and raise `TimeoutError` if the remote signer never responds.
- **NIP-44 unpad now rejects inconsistent padding.** Previously a declared
  plaintext length of zero was accepted (returning an empty message the spec
  forbids) and the total padded length was never checked against
  `calc_padded_len`, so non-canonical padding was silently accepted.
  Unpad now enforces the NIP-44 v2 rules and raises `ValueError`.

### Added
- Official NIP-06 known-answer test vectors (mnemonic -> private key hex ->
  nsec/npub) locking the cross-implementation contract.
- First bunker test suite: connect param correctness, npub normalization,
  secret handling, error responses, and timeout behavior.
