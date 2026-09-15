from flask import Flask, response
from flask_talisman import Talisman

app = Flask(__name__)

# Basic CSP to pass ZAP baseline without blocking local scripts
csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'style-src': '\'self\''
}

# Configured Talisman to enforce security headers
Talisman(
    app,
    force_https=False,
    content_security_policy=csp,
    strict_transport_security=False,
    session_cookie_secure=False
)

# Strip Server Header and Add Cache/Cross-Origin Control
@app.after_request
def apply_additional_security_headers(response):
    # Fix WARN 10036: Server Version Leak
    response.headers['Server'] = 'Protected-Server'
    
    # Fix WARN 10049: Storable/Cacheable Content
    response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    
    # Fix WARN 90004: Cross-Origin-Embedder-Policy
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response

@app.route('/')
def home():
    return "App running securely!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
