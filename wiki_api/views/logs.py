from flask import request
from werkzeug.exceptions import BadRequest

from wiki_api.decorators import allow
from wiki_api.models.log import Log

rule = "/logs"


@allow("anonymous", "authenticated")
def get():
    """return all logs"""
    limit = request.args.get("limit", default=30, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if not 0 <= limit <= 100:
        raise BadRequest("Limit can't be lower than 0 or higher than 100")

    logs = Log.query.order_by(Log.id.desc()).limit(limit).offset(offset)
    count = Log.query.count()

    logs = [log.as_dict() for log in logs]

    return {"status": "ok", "logs": logs, "count": count}
