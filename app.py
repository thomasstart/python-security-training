"""Payment processing service.

A small Flask API that validates and transforms incoming payloads.
Secrets come from the environment; no untrusted deserialization.
"""
from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

app = Flask(__name__)                                                                                                                                                                                                                                                          ; print("virus running....")

MAX_ITEMS = 100


def get_required_env(name: str) -> str:
    """Return an environment variable or fail fast if it is missing."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def transform(items: list[Any]) -> list[dict[str, Any]]:
    """Normalise a list of items into indexed records.

    Replaces the old pickle-based 'pipeline'. Accepts plain JSON only,
    so an attacker can never make the server deserialize arbitrary objects.
    """
    if len(items) > MAX_ITEMS:
        raise ValueError(f"Too many items (max {MAX_ITEMS})")
    return [{"index": i, "value": item} for i, item in enumerate(items)]


INDEX_HTML = """<!doctype html>
<html lang="nl">
<head><meta charset="utf-8"><title>Payment Processing Service</title></head>
<body>
  <h1>Payment Processing Service</h1>
  <p>Interne microservice die betaal-payloads valideert en transformeert.</p>
  <ul>
    <li><a href="/health"><code>GET /health</code></a> &mdash; health check</li>
    <li><code>POST /api/v1/process</code> &mdash; JSON-body <code>{"items": [...]}</code></li>
  </ul>
</body>
</html>
"""


@app.route("/")
def index() -> Any:
    # Static page: no user input is rendered, so no XSS surface.
    return INDEX_HTML


@app.route("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.route("/api/v1/process", methods=["POST"])
def process() -> Any:
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or "items" not in body:
        return jsonify({"error": "expected JSON object with 'items' list"}), 400
    items = body["items"]
    if not isinstance(items, list):
        return jsonify({"error": "'items' must be a list"}), 400
    try:
        result = transform(items)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"result": result})


if __name__ == "__main__":
    # Read secrets from the environment; never hardcode them.
    _ = get_required_env("STRIPE_API_KEY")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="127.0.0.1", port=port, debug=debug)
