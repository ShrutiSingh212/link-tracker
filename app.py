import os
import re
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, jsonify, abort

app = Flask(__name__)

links = {}  # code -> {"code", "url", "clicks", "expires_at"}
RESERVED = {"api", "health", "shorten", "static"}
ALIAS_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
COMMIT = os.getenv("RENDER_GIT_COMMIT", "local")[:7]


def is_valid_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


def make_code():
    while True:
        code = secrets.token_urlsafe(4)[:6]
        if code not in links and code not in RESERVED:
            return code


@app.route("/")
def home():
    return render_template("index.html", links=links.values(), commit=COMMIT)


@app.route("/shorten", methods=["POST"])
def shorten():
    url = request.form.get("url", "").strip()
    alias = request.form.get("alias", "").strip()

    if not is_valid_url(url):
        return "Enter a valid http(s) URL", 400

    if alias:
        if not ALIAS_RE.match(alias) or alias.lower() in RESERVED:
            return "Alias must be 3-20 letters, numbers, - or _", 400
        if alias in links:
            return "Alias already taken", 409
        code = alias
    else:
        code = make_code()

    minutes = request.form.get("expires_in", "").strip()
    expires_at = None
    if minutes:
        if not minutes.isdigit() or int(minutes) <= 0:
            return "Expiry must be a positive number of minutes", 400
        expires_at = datetime.utcnow() + timedelta(minutes=int(minutes))

    links[code] = {
        "code": code,
        "url": url,
        "clicks": 0,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }
    return redirect("/")


@app.route("/api/links")
def api_links():
    return jsonify(list(links.values()))


@app.route("/health")
def health():
    return {"status": "ok", "commit": COMMIT}


@app.route("/<code>")
def go(code):
    link = links.get(code)
    if not link:
        abort(404, "Short link not found")
    if link["expires_at"] and datetime.fromisoformat(link["expires_at"]) < datetime.utcnow():
        abort(410, "This link has expired")
    link["clicks"] += 1
    return redirect(link["url"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
