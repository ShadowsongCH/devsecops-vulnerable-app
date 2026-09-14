from flask import Flask, request
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("app.db")
    return conn


@app.route("/")
def home():
    return """
    <h1>DevSecOps Lab Application</h1>
    <p>Welcome to the vulnerable application.</p>
    <p><a href="/search?q=test">Search</a></p>
    """


@app.route("/search")
def search():
    query = request.args.get("q", "")

    conn = get_db()

    # Parameterized query prevents SQL injection
    sql = "SELECT * FROM users WHERE username LIKE ?"

    try:
        results = conn.execute(sql, (f"%{query}%",)).fetchall()
        return str(results)
    except Exception as e:
        return str(e)
    finally:
        conn.close()


if __name__ == "__main__":
    # Required for Flask to accept connections through the Docker container network interface.
    app.run(host="0.0.0.0", port=5000)  # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host
