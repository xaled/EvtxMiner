from .config import TITLES_CSV
import csv

_titles_db: dict | None = None


def _load_titles_db():
    with open(TITLES_CSV) as fin:
        csv_reader = csv.DictReader(fin)
        return {(row['channel'], row['provider'], int(row['event_id'])): row['title'] for row in csv_reader}


def get_titles_db():
    global _titles_db
    if _titles_db is None:
        _titles_db = _load_titles_db()

    return _titles_db


def get_title(channel, provider, event_id):
    return get_titles_db().get((channel, provider, event_id), None)
