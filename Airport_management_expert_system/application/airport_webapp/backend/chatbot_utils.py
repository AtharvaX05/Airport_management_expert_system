import os
import re
from datetime import datetime


def parse_date(text):
    """Parse a date from text. Returns a datetime.date or None."""
    if not text:
        return None

    months = {m.lower(): i for i, m in enumerate(["", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]) }
    # look for yyyy-mm-dd
    m = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", text)
    if m:
        try:
            return datetime.fromisoformat(m.group(1)).date()
        except Exception:
            pass

    # look for '15th october' or '15 october'
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)", text, flags=re.IGNORECASE)
    if m:
        try:
            day = int(m.group(1))
        except Exception:
            return None
        mon = m.group(2).lower()
        mon_num = months.get(mon)
        if mon_num:
            year = datetime.utcnow().year
            try:
                return datetime(year, mon_num, day).date()
            except Exception:
                pass

    return None


def parse_flight_token(text):
    """Extract a flight-like token from text (e.g., 'AI101', 'BOEING343', '343')."""
    if not text:
        return None

    # try common flight formats: letters+digits (2-4 letters), word + digits, or just digits
    m = re.search(r"([A-Za-z]{2,4}\s*-?\s*\d{1,4})", text)
    if m:
        return re.sub(r"\s+|-", "", m.group(1)).upper()
    m = re.search(r"([A-Za-z]+\s+\d{1,4})", text)
    if m:
        return m.group(1).replace(" ", "").upper()
    m = re.search(r"\b(\d{2,4})\b", text)
    if m:
        return m.group(1)
    return None


def find_in_sql_dump(flight_id, date_obj=None, dump_path=None):
    """
    Search a SQL dump file for flights and return a datetime for ScheduledDeparture when matched.
    - flight_id: token to match against FlightNumber (case-insensitive, substring)
    - date_obj: optional date to match the departure date
    - dump_path: optional path to a .sql file; if None, defaults to airlineexpertsystem_dump.sql in this folder
    Returns a datetime or None.
    """
    if dump_path is None:
        dump_path = os.path.join(os.path.dirname(__file__), "airlineexpertsystem_dump.sql")
    if not os.path.exists(dump_path):
        return None

    with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # find INSERTs into `flights`
    inserts = re.findall(r"INSERT INTO `flights`.*?VALUES\s*(\(.+?\));", content, flags=re.IGNORECASE | re.DOTALL)
    tuples = []
    for ins in inserts:
        parts = re.split(r"\),\s*\(", ins.strip())
        for p in parts:
            p = p.strip()
            if not p:
                continue
            p = p.lstrip('(').rstrip(')')
            tuples.append(p)

    for t in tuples:
        # capture FlightNumber (2nd field) and ScheduledDeparture (5th field) heuristically
        m = re.match(r"\s*\d+\s*,\s*'(?P<flight>[^']*)'\s*,\s*\d+\s*,\s*\d+\s*,\s*'(?P<dep>[^']*)'", t)
        if not m:
            continue
        flight_val = m.group('flight')
        dep_val = m.group('dep')

        if flight_id:
            if flight_id.upper() in flight_val.upper() or flight_val.upper() in str(flight_id).upper():
                try:
                    dep_dt = datetime.fromisoformat(dep_val)
                    if date_obj:
                        if dep_dt.date() == date_obj:
                            return dep_dt
                    else:
                        return dep_dt
                except Exception:
                    continue
        else:
            try:
                dep_dt = datetime.fromisoformat(dep_val)
                if date_obj and dep_dt.date() == date_obj:
                    return dep_dt
            except Exception:
                continue

    return None
