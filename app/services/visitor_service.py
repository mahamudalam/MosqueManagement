import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import request

from app import db
from app.models import VisitorCounter, VisitorLog

from user_agents import parse


IST = ZoneInfo("Asia/Kolkata")


def track_visitor():
    """
    Tracks unique visitors using browser cookie.
    Returns:
        visitor_uuid
        is_new_visitor
        total_visitors
    """

    visitor_uuid = request.cookies.get("visitor_uuid")

    counter = VisitorCounter.query.first()

    if counter is None:
        counter = VisitorCounter(
            id=1,
            total_visitors=0
        )
        db.session.add(counter)
        db.session.commit()

    is_new = False

    # Existing Cookie
    if visitor_uuid:

        visitor = VisitorLog.query.filter_by(
            visitor_uuid=visitor_uuid
        ).first()

        if visitor:

            visitor.last_visit = datetime.now(IST)
            visitor.visit_count += 1

            db.session.commit()

            return visitor_uuid, False, counter.total_visitors

    # New Visitor
    visitor_uuid = str(uuid.uuid4())

    user_agent = parse(request.headers.get("User-Agent"))

    visitor = VisitorLog(

        visitor_uuid=visitor_uuid,

        ip_address=request.remote_addr,

        user_agent=request.headers.get("User-Agent"),

        browser=user_agent.browser.family,

        operating_system=user_agent.os.family,

        device=user_agent.device.family,

        first_visit=datetime.now(IST),

        last_visit=datetime.now(IST),

        visit_count=1
    )

    db.session.add(visitor)

    counter.total_visitors += 1

    db.session.commit()

    return visitor_uuid, True, counter.total_visitors