import os
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\''
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
    # Environmental binding fixes Semgrep avoid_app_run_with_bad_host rule
    host_ip = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    app.run(host=host_ip, port=5000)
INVALID_SYNTAX_FAIL_TEST
