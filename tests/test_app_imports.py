from datetime import date, datetime

from app import create_app, db
from app.models import FridayDonation, Member, ContributionMode
from app.services.friday_report_service import FridayReportService


def test_app_creates_without_errors():
    app = create_app()
    assert app is not None


def test_user_management_routes_are_available():
    app = create_app()
    client = app.test_client()

    response = client.get("/users")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_friday_report_page_includes_search_filters():
    app = create_app()
    client = app.test_client()

    response = client.get("/reports/friday-report?search=1")

    assert response.status_code == 200
    assert b"Search Report" in response.data
    assert b"All Members" in response.data
    assert b"Status" in response.data


def test_friday_report_service_collects_paid_dates_and_mode_counts():
    app = create_app()

    with app.app_context():
        member = Member(
            name="Test Member",
            phone=f"9999999{datetime.now().microsecond}",
            address="Test Address",
            imam_salary_contri=0,
            join_date=date(2024, 1, 1),
        )
        second_member = Member(
            name="Another Member",
            phone=f"8888888{datetime.now().microsecond + 1}",
            address="Another Address",
            imam_salary_contri=0,
            join_date=date(2024, 1, 1),
        )
        db.session.add_all([member, second_member])
        db.session.flush()

        donation1 = FridayDonation(
            member_id=member.id,
            donation_date=date(2024, 1, 5),
            amount=100,
            status="Paid",
            contribution_mode=ContributionMode.MONEY,
            contribution_date=date(2024, 1, 5),
            remarks="",
        )
        donation2 = FridayDonation(
            member_id=member.id,
            donation_date=date(2024, 1, 12),
            amount=0,
            status="Paid",
            contribution_mode=ContributionMode.RICE,
            contribution_date=date(2024, 1, 12),
            remarks="",
        )
        db.session.add_all([donation1, donation2])
        db.session.commit()

        service = FridayReportService(year=2024, month=1, member_id=member.id)
        data = service.generate()

        summary = data["member_summary"]

        assert summary["paid_dates"] == ["05-Jan-2024", "12-Jan-2024"]
        assert summary["money_count"] == 1
        assert summary["rice_count"] == 1
        assert data["report_data"][0]["contribution_mode"] == "Money"
        assert len(data["members"]) >= 2
        assert any(item.id == member.id for item in data["members"])
        assert any(item.id == second_member.id for item in data["members"])
        assert len(data["report_data"]) >= 1


def test_friday_report_service_lists_due_friday_dates_for_due_months():
    app = create_app()

    with app.app_context():
        member = Member(
            name="Due Date Member",
            phone=f"7777777{datetime.now().microsecond}",
            address="Due Address",
            imam_salary_contri=0,
            join_date=date(2024, 1, 1),
        )
        db.session.add(member)
        db.session.flush()
        db.session.commit()

        service = FridayReportService(year=2024, member_id=member.id)
        data = service.generate()

        summary = data["member_summary"]

        assert "05-Jan-2024" in summary["due_months"]
        assert "12-Jan-2024" in summary["due_months"]


def test_friday_report_service_returns_structured_due_members_summary():
    app = create_app()

    with app.app_context():
        member = Member(
            name="Structured Due Member",
            phone=f"6666666{datetime.now().microsecond}",
            address="Structured Address",
            imam_salary_contri=0,
            join_date=date(2024, 1, 1),
        )
        db.session.add(member)
        db.session.flush()
        db.session.commit()

        service = FridayReportService(year=2024, month=1)
        data = service.generate()

        members_summary = data["due_members_summary"]["members"]

        assert members_summary
        assert any(item["member_name"] == member.name for item in members_summary)
        assert any("January" in item["due_months"] for item in members_summary)


def test_friday_report_service_counts_total_paid_due_and_advance_fridays():
    app = create_app()

    with app.app_context():
        member = Member(
            name="Summary Count Member",
            phone=f"5555555{datetime.now().microsecond}",
            address="Summary Address",
            imam_salary_contri=0,
            join_date=date(2026, 1, 1),
        )
        db.session.add(member)
        db.session.flush()

        db.session.add_all([
            FridayDonation(
                member_id=member.id,
                donation_date=date(2026, 1, 2),
                amount=100,
                status="Paid",
                contribution_mode=ContributionMode.MONEY,
                contribution_date=date(2026, 1, 2),
                remarks="",
            ),
            FridayDonation(
                member_id=member.id,
                donation_date=date(2026, 1, 9),
                amount=0,
                status="Due",
                contribution_mode=ContributionMode.MONEY,
                contribution_date=date(2026, 1, 9),
                remarks="",
            ),
            FridayDonation(
                member_id=member.id,
                donation_date=date(2026, 8, 7),
                amount=100,
                status="Paid",
                contribution_mode=ContributionMode.MONEY,
                contribution_date=date(2026, 8, 7),
                remarks="",
            ),
        ])
        db.session.commit()

        service = FridayReportService(year=2026, member_id=member.id)
        data = service.generate()
        summary = data["member_summary"]

        assert summary["total_fridays"] == 52
        assert summary["paid_friday_count"] == 1
        assert summary["due_friday_count"] == 1
        assert summary["advance_friday_count"] == 1
