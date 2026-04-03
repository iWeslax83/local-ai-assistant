import pytest
from core.db import init_db, get_db


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = get_db(db_path)
    yield conn
    conn.close()
