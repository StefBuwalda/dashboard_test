# import requests as r
from flask import jsonify, render_template, send_file, abort
from poll_services import start_async_loop
from mem import services, app, db
import threading
from flask_migrate import upgrade, stamp
from pathlib import Path
from models import service, log
from typing import Any, Optional, cast
import json
from datetime import datetime, timezone, timedelta
from config import timeout


# Prepares log data for chart.js chart
def prepare_chart_data(
    logs: list[log],
) -> tuple[list[str], list[Optional[int]]]:
    if len(logs) <= 0:  # Return empty if there are no logs
        return ([], [])

    x = [logs[0].dateCreatedUTC().isoformat()]
    y = [logs[0].ping]

    for i in range(1, len(logs)):
        log1 = logs[i]
        log2 = logs[i - 1]

        # Check if the gap in points exceeds a threshold
        if (abs(log1.dateCreatedUTC() - log2.dateCreatedUTC())) > timedelta(
            milliseconds=1.5 * (timeout + 1000)
        ):
            x.append(log2.dateCreatedUTC().isoformat())
            y.append(None)

        x.append(log1.dateCreatedUTC().isoformat())
        y.append(log1.ping)
    return (x, y)


# Init and upgrade
with app.app_context():
    # Check if DB file is missing
    if not (Path("./instance/app.db").is_file()):
        with app.app_context():
            db.create_all()
        stamp()
    # Upgrade db if any new migrations exist
    upgrade()

with app.app_context():
    if not db.session.query(service).first():
        for s in services:
            db.session.add(
                service(
                    url=s.url,
                    label=s.label,
                    public_access=s.public,
                    ping_method=s.ping_type,
                )
            )
        db.session.commit()


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/chart/<int:id>")
def chart(id: int):
    with app.app_context():
        logs = []
        s = db.session.query(service).filter_by(id=id).first()
        if s:
            logs = cast(
                list[log],
                s.logs.order_by(log.dateCreated.desc())  # type: ignore
                .limit(300)
                .all(),
            )
        else:
            return abort(code=403)
    x, y = prepare_chart_data(logs=logs)

    now = datetime.now(timezone.utc)
    max_ = now
    min_ = now - timedelta(hours=1)
    return render_template(
        "chart.html",
        dates=x,
        values=json.dumps(y),
        min=min_.isoformat(),
        max=max_.isoformat(),
    )


@app.route("/api/status")
def status():
    results: list[dict[str, Any]] = []
    with app.app_context():
        a = db.session.query(service).all()
        for s in a:
            b = cast(
                Optional[log],
                s.logs.order_by(
                    log.dateCreated.desc()  # type: ignore
                ).first(),
            )
            if b:
                results.append(s.to_dict() | b.to_dict())

    return jsonify(results)


@app.route("/favicon.svg")
def favicon():
    return send_file("/static/favicon.svg")


# Only run if directly running file
if __name__ == "__main__":
    t = threading.Thread(target=start_async_loop, daemon=True)
    t.start()

    # Run flask app
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False)
