# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CA-GEN is a local web-based Certificate Authority (CA) management tool built with Flask. It enables creation and management of a PKI hierarchy: Root CAs → Intermediate CAs → Leaf certificates, with SAN (Subject Alternative Name) support for both DNS names and IP addresses.

## Running the Application

```bash
# Install dependencies (one-time)
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Run
./venv/bin/python app.py
```

The app runs on `http://127.0.0.1:5000` in debug mode.

## Architecture

Two core files handle all logic:

**[app.py](app.py)** — Flask routes only; no business logic. Seven routes:
- `/` — Dashboard listing files in `ca_storage/`
- `/create_root_ca` — Generate self-signed root CA
- `/create_csr` — Generate RSA key + CSR with optional SANs
- `/sign_csr` — Sign a CSR with an existing CA (supports "Is Intermediate CA" flag)
- `/verify_cert` — Verify cert signature against issuer
- `/view/<filename>` — Parsed cert details
- `/download/<filename>` — File download

**[crypto_utils.py](crypto_utils.py)** — All cryptographic logic in the `CryptoUtils` class. Key methods:
- `generate_key()` → 2048-bit RSA key
- `create_root_ca()` → self-signed cert with `BasicConstraints(ca=True)`
- `create_csr()` → CSR with optional `SubjectAlternativeName` (DNS + IP)
- `sign_csr()` → signs CSR using CA key; sets `BasicConstraints(ca=True)` if intermediate
- `verify_cert_signature()` → PKCS#1v15 verification against issuer public key
- `get_cert_details()` → extracts subject, issuer, SAN, validity, fingerprint

**Storage**: All generated `.key`, `.csr`, `.crt` files go to `ca_storage/` (git-ignored).

**Templates** ([templates/](templates/)): Jinja2 with a shared `base.html` layout. Each route has a corresponding template form.

## Cryptographic Defaults

| Parameter | Value |
|-----------|-------|
| RSA key size | 2048 bits |
| Hash | SHA256 |
| Root CA validity | 3650 days |
| Leaf cert validity | 365 days |
| Signature scheme | PKCS#1 v1.5 |

## Dependencies

```
Flask==3.0.0
cryptography==41.0.7
```
