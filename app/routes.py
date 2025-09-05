from flask import Blueprint, render_template, abort, jsonify, send_file, json
from typing import cast, Optional, Any
from datetime import datetime, timedelta, timezone
from config import timeout
from .models import service, log
from app import app, db

bp = Blueprint(
    "main",
    "__name__",
    url_prefix="/",
    static_folder="static",
)


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


@bp.route("/")
def homepage():
    return render_template("home.html")


@bp.route("/chart/<int:id>")
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


@bp.route("/api/status")
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


@bp.route("/favicon.svg")
def favicon():
    return send_file("/static/favicon.svg")
