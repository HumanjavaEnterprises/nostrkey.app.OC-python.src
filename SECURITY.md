# Security Policy

`nostrkey` is a Python SDK for Nostr **identity and signing** — it generates and
handles private keys (nsec), signs events, and runs a NIP-46 bunker. Security
reports are taken seriously and handled with priority.

> **Always run the latest version.** Security and key-handling fixes ship in the
> newest release on PyPI: `pip install --upgrade nostrkey`.

## Reporting a vulnerability

**Please report security issues privately — do not open a public GitHub issue.**

- Preferred: [GitHub private vulnerability reporting](https://github.com/HumanjavaEnterprises/nostrkey.app.OC-python.src/security/advisories/new) ("Report a vulnerability").
- Or email **security@humanjava.com** with details and reproduction steps.
- For sensitive reports, you may encrypt to the maintainer's Nostr key (NIP-44 DM); request the current npub in your first email.

Please include:
- A clear description and the impact (what an attacker could do).
- Steps to reproduce, or a proof of concept.
- Affected version(s) and Python version.

### What to expect
- Acknowledgement within **3 business days**.
- An initial assessment and severity within **7 business days**.
- Coordinated disclosure: we'll agree a timeline with you before any public detail, and credit you (if you wish) once a fix ships.

## Supported versions

Security fixes target the **latest published version** on PyPI. Older versions
are not patched — please update before reporting.

## Scope notes

- Key generation uses the `secrets` CSPRNG and the `cryptography` package's
  secp256k1 — reports about weak entropy sources or key derivation are in scope
  and high priority.
- The gated reveal path (`export_nsec` + `NOSTRKEY_REVEAL_CODE`) is a security
  boundary — bypasses are in scope.
- Vulnerabilities in dependencies should go to the upstream project first;
  tell us too if `nostrkey`'s usage of the dependency makes it exploitable.
