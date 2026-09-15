from flask import Flask, make_response
from flask_talisman import Talisman

app = Flask(__name__)

csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\''
}

# Apply Talisman for headers without HTTPS redirection on localhost
Talisman(
    app,
    force_https=False,
    content_security_policy=csp,
    strict_transport_security=False,
    session_cookie_secure=False
)

@app.after_request
def apply_additional_security_headers(response):
    response.headers['Server'] = 'Protected-Server'
    response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response

@app.route('/')
def home():
    return "App running securely!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
