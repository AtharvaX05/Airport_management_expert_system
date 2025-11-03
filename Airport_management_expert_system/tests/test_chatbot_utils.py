import os
import tempfile
from datetime import datetime

from application.airport_webapp.backend.chatbot_utils import parse_date, parse_flight_token, find_in_sql_dump


def test_parse_date_iso():
    assert parse_date("2025-10-15") == datetime.fromisoformat("2025-10-15").date()


def test_parse_date_natural():
    d = parse_date("when is it on 15th October")
    assert d is not None
    assert d.day == 15


def test_parse_flight_token():
    assert parse_flight_token("when will AI101 depart?") == "AI101"
    assert parse_flight_token("boeing 343 on 15th") == "BOEING343"
    assert parse_flight_token("flight 343") == "343"


def test_find_in_sql_dump(tmp_path):
    # Create a temporary SQL dump with a flights insert
    dump_file = tmp_path / "tmp_dump.sql"
    content = """
    INSERT INTO `flights` VALUES (1,'BOEING343',1,2,'2025-10-15T08:30:00','2025-10-15T12:00:00',3,'Scheduled');
    """
    dump_file.write_text(content)

    dep = find_in_sql_dump("BOEING343", datetime.fromisoformat("2025-10-15").date(), dump_path=str(dump_file))
    assert dep is not None
    assert dep.year == 2025 and dep.month == 10 and dep.day == 15
