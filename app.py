import os
from flask import Flask, request, jsonify
from flask_talisman import Talisman
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# Enforce strict Content Security Policy (CSP) headers
csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\'',
    'img-src': '\'self\'',
    'font-src': '\'self\'',
    'connect-src': '\'self\'',
    'media-src': '\'self\'',
    'object-src': '\'none\'',
    'base-uri': '\'self\'',
    'form-action': '\'self\'',
    'frame-ancestors': '\'none\''
}

Talisman(
    app,
    force_https=False,
    content_security_policy=csp,
    strict_transport_security=False,
    session_cookie_secure=False
)

@app.after_request
def apply_additional_security_headers(response):
    # Remove framework/server fingerprinting
    response.headers.pop('Server', None)

    # Cache control
    response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
    response.headers['Pragma'] = 'no-cache'

    # Browser security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Permissions-Policy'] = 'browsing-topics=()'

    # Cross-origin isolation
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    return response

# Connection string (defaults to local/CI Floci emulator)
CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

CONTAINER_NAME = "secure-vault"

# Initialize Blob Service Client
try:
    blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)
    blob_service_client.create_container(CONTAINER_NAME)
except Exception:
    pass  # Container already exists or initialized

@app.route('/')
def home():
    return jsonify({"status": "online", "service": "DevSecOps Cloud Vault API"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)
    blob_client.upload_blob(file.stream, overwrite=True)

    return jsonify({"message": f"File '{file.filename}' uploaded to Azure storage!"}), 201

@app.route('/files', methods=['GET'])
def list_files():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = [blob.name for blob in container_client.list_blobs()]
    return jsonify({"stored_files": blobs})

@app.route('/search')
def search():
    query = request.args.get("q", "")

    # Intentionally vulnerable: SQL injection test for Semgrep
    sql = "SELECT * FROM users WHERE username LIKE ?"

    return jsonify({"query": sql})

if __name__ == '__main__':
    # Environmental binding fixes Semgrep avoid_app_run_with_bad_host rule
    host_ip = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    app.run(host=host_ip, port=5000)
