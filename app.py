from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from crypto_utils import CryptoUtils
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_purposes'

@app.route('/')
def index():
    # List available files in storage
    files = []
    if os.path.exists(CryptoUtils.STORAGE_DIR):
        files = sorted(os.listdir(CryptoUtils.STORAGE_DIR))
    return render_template('index.html', files=files)

@app.route('/create_root_ca', methods=['GET', 'POST'])
def create_root_ca():
    if request.method == 'POST':
        cn = request.form['common_name']
        org = request.form['organization']
        country = request.form['country']
        filename_base = request.form['filename']
        valid_days = int(request.form.get('valid_days', 3650))

        key, cert = CryptoUtils.create_root_ca(cn, org, country, valid_days=valid_days)
        CryptoUtils.save_key(key, f"{filename_base}.key")
        CryptoUtils.save_cert(cert, f"{filename_base}.crt")
        
        flash(f'Root CA {cn} created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_ca.html', type='Root')

@app.route('/create_csr', methods=['GET', 'POST'])
def create_csr():
    if request.method == 'POST':
        cn = request.form['common_name']
        org = request.form['organization']
        country = request.form['country']
        filename_base = request.form['filename']
        sans_input = request.form.get('sans', '')
        sans = [s.strip() for s in sans_input.split(',')] if sans_input else []
        
        # In a real app, user might want to download the key immediately
        # Here we save it to the server for the user to download later or use
        key, csr = CryptoUtils.create_csr(cn, org, country, sans=sans)
        CryptoUtils.save_key(key, f"{filename_base}.key")
        
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)
        with open(os.path.join(CryptoUtils.STORAGE_DIR, f"{filename_base}.csr"), "wb") as f:
            f.write(csr_pem)

        flash(f'CSR for {cn} created.', 'success')
        return redirect(url_for('index'))
    return render_template('create_csr.html')

@app.route('/sign_csr', methods=['GET', 'POST'])
def sign_csr():
    # Get list of potential CAs (files ending in .crt) and CSRs
    if not os.path.exists(CryptoUtils.STORAGE_DIR):
        os.makedirs(CryptoUtils.STORAGE_DIR)
        
    files = os.listdir(CryptoUtils.STORAGE_DIR)
    ca_certs = [f for f in files if f.endswith('.crt')]
    csrs = [f for f in files if f.endswith('.csr')]

    if request.method == 'POST':
        csr_file = request.form['csr_file']
        ca_cert_file = request.form['ca_cert_file']
        # Assumption: Key file has same base name as cert file but .key extension
        ca_key_file = ca_cert_file.replace('.crt', '.key')
        
        if not os.path.exists(os.path.join(CryptoUtils.STORAGE_DIR, ca_key_file)):
             flash(f'Error: Private key {ca_key_file} not found for selected CA.', 'error')
             return redirect(url_for('sign_csr'))

        is_ca = 'is_ca' in request.form
        valid_days = int(request.form.get('valid_days', 365))
        output_filename = request.form['output_filename']

        with open(os.path.join(CryptoUtils.STORAGE_DIR, csr_file), 'r') as f:
            csr_pem = f.read()

        cert = CryptoUtils.sign_csr(
            csr_pem, 
            ca_cert_file, 
            ca_key_file, 
            valid_days=valid_days, 
            is_ca=is_ca
        )
        CryptoUtils.save_cert(cert, f"{output_filename}.crt")
        
        flash(f'Certificate {output_filename}.crt signed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('sign_csr.html', ca_certs=ca_certs, csrs=csrs)

@app.route('/verify_cert', methods=['GET', 'POST'])
def verify_cert():
    if not os.path.exists(CryptoUtils.STORAGE_DIR):
        os.makedirs(CryptoUtils.STORAGE_DIR)
        
    files = os.listdir(CryptoUtils.STORAGE_DIR)
    certs = [f for f in files if f.endswith('.crt')]

    if request.method == 'POST':
        cert_file = request.form['cert_file']
        issuer_file = request.form['issuer_file']
        
        is_valid, message = CryptoUtils.verify_cert_signature(cert_file, issuer_file)
        
        category = 'success' if is_valid else 'error'
        flash(f'Verification result for {cert_file} against {issuer_file}: {message}', category)
        return redirect(url_for('verify_cert'))

    return render_template('verify_cert.html', certs=certs)

def _safe_storage_path(filename):
    """Reject traversal; return an absolute path inside STORAGE_DIR or None."""
    if filename != os.path.basename(filename):
        return None
    storage_root = os.path.realpath(CryptoUtils.STORAGE_DIR)
    candidate = os.path.realpath(os.path.join(storage_root, filename))
    if os.path.commonpath([storage_root, candidate]) != storage_root:
        return None
    if not os.path.isfile(candidate):
        return None
    return candidate

@app.route('/view/<filename>')
def view_cert_details(filename):
    if not filename.endswith('.crt'):
        flash('Can only view certificate details (.crt files).', 'error')
        return redirect(url_for('index'))

    if _safe_storage_path(filename) is None:
        flash('File not found.', 'error')
        return redirect(url_for('index'))

    details = CryptoUtils.get_cert_details(filename)
    if not details:
        flash('Error parsing certificate.', 'error')
        return redirect(url_for('index'))

    return render_template('view_cert.html', filename=filename, details=details)

@app.route('/download/<filename>')
def download_file(filename):
    path = _safe_storage_path(filename)
    if path is None:
        flash('File not found.', 'error')
        return redirect(url_for('index'))
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
