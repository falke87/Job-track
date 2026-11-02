"""Tests for the database layer. Run with:  pytest"""

import os
import tempfile

import pytest

from jobtrack.db import Database
from jobtrack.models import Application


@pytest.fixture
def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = Database(path)
    yield database
    database.close()
    os.remove(path)


def _sample(company="Acme", position="C++ Developer"):
    return Application(id=None, company=company, position=position)


def test_add_and_get(db):
    new_id = db.add(_sample())
    app = db.get(new_id)
    assert app is not None
    assert app.company == "Acme"
    assert app.status == "applied"
    assert app.applied_on != ""  # defaulted to today


def test_list_and_filter(db):
    db.add(_sample("A"))
    second = db.add(_sample("B"))
    db.set_status(second, "interview")
    assert len(db.list()) == 2
    assert len(db.list(status="interview")) == 1
    assert db.list(status="interview")[0].company == "B"


def test_set_status(db):
    new_id = db.add(_sample())
    assert db.set_status(new_id, "offer") is True
    assert db.get(new_id).status == "offer"
    assert db.set_status(9999, "offer") is False


def test_delete(db):
    new_id = db.add(_sample())
    assert db.delete(new_id) is True
    assert db.get(new_id) is None
    assert db.delete(new_id) is False


def test_invalid_status_rejected(db):
    bad = Application(id=None, company="X", position="Y", status="nope")
    with pytest.raises(ValueError):
        db.add(bad)


def test_empty_company_rejected(db):
    with pytest.raises(ValueError):
        db.add(Application(id=None, company="  ", position="Y"))
