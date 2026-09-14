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

    # Intentionally vulnerable SQL query
    sql = "SELECT * FROM users WHERE username LIKE '%" + query + "%'"

    try:
        results = conn.execute(sql).fetchall()
        return str(results)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
