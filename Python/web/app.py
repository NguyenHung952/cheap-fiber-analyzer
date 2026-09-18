from __future__ import annotations

from flask import Flask, jsonify, render_template, request

import sys
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
PYTHON_DIR = WEB_DIR.parent
PROJECT_DIR = PYTHON_DIR.parent

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from database import get_events, get_measurements, get_status, init_db


app = Flask(
    __name__,
    template_folder=str(WEB_DIR / "templates"),
    static_folder=str(WEB_DIR / "static"),
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def api_health():
    return jsonify({"ok": True, "service": "cheap-fiber-web"})


@app.get("/api/status")
def api_status():
    row = get_status()
    if row is None:
        return jsonify({"available": False})

    return jsonify(
        {
            "available": True,
            "status": dict(row),
        }
    )


@app.get("/api/measurements")
def api_measurements():
    try:
        limit = max(1, min(int(request.args.get("limit", 20)), 200))
    except Exception:
        limit = 20

    rows = get_measurements(limit)
    return jsonify({"measurements": [dict(row) for row in rows]})


@app.get("/api/events")
def api_events():
    try:
        limit = max(1, min(int(request.args.get("limit", 20)), 200))
    except Exception:
        limit = 20

    rows = get_events(limit)
    return jsonify({"events": [dict(row) for row in rows]})


if __name__ == "__main__":
    init_db()
    print("Cheap Fiber Analyzer Web running at http://127.0.0.1:5000")
    print(f"Project directory: {PROJECT_DIR}")
    app.run(host="127.0.0.1", port=5000, debug=False)
