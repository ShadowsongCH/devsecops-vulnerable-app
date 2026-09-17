import os
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# Connection string (defaults to local/CI Floci emulator)
CONN_STR = os.getenv(
    "CONN_STR",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=REDACTED-DEV-SECRET;BlobEndpoint=http://localhost:4577/devstoreaccount1;"
)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
