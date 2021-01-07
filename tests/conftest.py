import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import List, Optional, Tuple

from shopping_list.app.model import Base


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
