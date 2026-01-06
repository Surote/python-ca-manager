# Python CA Manager

A local web-based Certificate Authority (CA) management tool built with Flask and Cryptography.

## Features

-   **Create Root CA**: Generate self-signed Root Certificate Authorities.
-   **Create Intermediate CA**: Generate CSRs and sign them as Intermediate CAs.
-   **Generate CSR**: Create Certificate Signing Requests for end entities (websites, etc.).
-   **Sign CSR**: Sign CSRs using your Root or Intermediate CAs.
-   **SAN Support**: Add Subject Alternative Names (DNS) to CSRs and Certificates.
-   **Verify Certificates**: Check if a certificate was signed by a specific Issuer.
-   **File Management**: Download generated keys, certificates, and CSRs.

## Installation

1.  **Clone/Open the repository**:
    ```bash
    cd /path/to/CA-GEN
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    ```

3.  **Install Dependencies**:
    ```bash
    ./venv/bin/pip install -r requirements.txt
    ```

## Usage

1.  **Start the Application**:
    ```bash
    ./venv/bin/python app.py
    ```

2.  **Open Browser**:
    Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

3.  **Workflow**:
    -   Create a **Root CA**.
    -   Create a **CSR** for an intermediate (e.g., `int-ca`).
    -   **Sign** the `int-ca.csr` with the Root CA (Enable "Is Intermediate CA" checkbox).
    -   Create a **CSR** for a website (e.g., `example.com`) with SANs.
    -   **Sign** the `example.com.csr` with the Intermediate CA (Leave "Is Intermediate CA" unchecked).
    -   **Download** the resulting `.crt` files.

## Project Structure

-   `app.py`: Main Flask application.
-   `crypto_utils.py`: Cryptographic logic (Key/Cert generation, Signing, Verification).
-   `templates/`: HTML templates.
-   `static/`: CSS styles.
-   `ca_storage/`: Directory where generated keys and certificates are stored (created automatically).

## License

Copyright (c) 2026 swongpai. Local Development Tool.
