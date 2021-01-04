import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shopping_list.app.model import Base


@pytest.fixture
def sqlite_session_factory():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    sm = sessionmaker(bind=engine)
    session = sm()
    session.execute("PRAGMA foreign_keys=ON")
    session.commit()
    session.close()
    yield sm
