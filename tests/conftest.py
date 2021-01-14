import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Any, List, Optional, Tuple

from shopping_list.app.app import create_app
from shopping_list.app.model import Base
from shopping_list.app.repo import ImageStore
from shopping_list.app.unit_of_work import UoW


class MockStore(ImageStore):
    def __init__(self, placeholder: Any):
        super().__init__()

    def get(self, img_id: int):
        return None

    def add(self, img: Any, img_id: int):
        pass

    def close(self):
        pass


def insert_ingredient(session: Session, ing_name: str, category: str, unit: Optional[str] = None) -> int:
    result = session.execute(
        """INSERT INTO 'shlist.ingredient' (ing_name, category, unit)
        VALUES(:ing_name, :category, :unit)""",
        dict(ing_name=ing_name, category=category, unit=unit)
    )
    session.commit()
    return result.lastrowid


def insert_recipe(session: Session, title: str, description: Optional[str] = None) -> int:
    result = session.execute(
        """INSERT INTO 'shlist.recipe' (title, description)
        VALUES(:title, :description)""",
        dict(title=title, description=description)
    )
    session.commit()
    return result.lastrowid


def insert_recipe_ingredient(
        session: Session,
        title: str,
        ingredients: List[Tuple[str, str, str, float]]
):
    recipe_id = insert_recipe(session, title)
    ingredient_ids = []
    for ing in ingredients:
        ingredient_ids.append(
            (insert_ingredient(session, ing[0], ing[1], ing[2]), ing[3])
        )
    for i in ingredient_ids:
        session.execute(
            """INSERT INTO 'shlist.recipe_ingredient' (recipe_id, ingredient_id, amount)
            VALUES(:recipe_id, :ingredient_id, :amount)""",
            dict(recipe_id=recipe_id, ingredient_id=i[0], amount=i[1])
        )


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


@pytest.fixture
def sqlite_prefill_db(sqlite_session_factory):
    session = sqlite_session_factory()
    _ = insert_ingredient(session, 'salt', 'spice')
    _ = insert_ingredient(session, 'feta cheese', 'dairy', 'g')
    _ = insert_recipe(session, 'Pasta with feta cheese')
    insert_recipe_ingredient(
        session,
        'Risotto',
        [
            ('onion', 'vegetable', 'pc', 1),
            ('risotto rice', 'side_dish', 'g', 300),
            ('zucchini', 'vegetable', 'pc', 1),
            ('brooth', 'spice', None, None),
            ('ricotta', 'dairy', 'g', 200),
        ]
    )
    session.commit()
    session.close()


@pytest.fixture
def uow_with_mocked_image_store(sqlite_session_factory, mocker):
    mocker.patch('shopping_list.app.unit_of_work.create_img_store', return_value=MockStore(None))
    yield UoW(sqlite_session_factory, None, None)


@pytest.fixture
def app(uow_with_mocked_image_store):
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'random-key-for-testing',
    })
    app.uow = uow_with_mocked_image_store
    yield app


@pytest.fixture
def client(app):
    yield app.test_client()
