from __future__ import annotations  # Needed for __enter__
from sqlalchemy.orm import sessionmaker
from typing import Optional

from shopping_list.app.config import MONGO_CONNECTION, PSQL_SESSION_FACTORY
from shopping_list.app.repo import MongoStore, SqlAlchemyRepository


class UoW:
    def __init__(
        self,
        session_factory: sessionmaker = PSQL_SESSION_FACTORY,
        store_details: Tuple[str, ...] = MONGO_CONNECTION
    ):
        self.session_factory = session_factory
        self.all_ingredients = None
        self.store_details = store_details

    def __enter__(self) -> UoW:
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        self.img_store = MongoStore(*self.store_details)
        # Initialize only the first time the uow is used (and extend it with new ingredients in add_recipe)
        if self.all_ingredients is None:
            self.all_ingredients = self.repo.get_all_ingredients_as_dict()
        return self

    def __exit__(self, *args):
        self.session.rollback()
        self.session.close()
        self.img_store.close()

    def commit(self):
        self.session.commit()

    def append_ingredient(self, ing_name: str, unit: Optional[str] = None, category: Optional[str] = None):
        self.all_ingredients[ing_name] = {'unit': unit, 'category': category}
