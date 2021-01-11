from __future__ import annotations  # Needed for __enter__
from sqlalchemy.orm import sessionmaker
from typing import Dict, Optional

from shopping_list.app.config import PSQL_SESSION_FACTORY, REDIS_CONNECTION
from shopping_list.app.repo import create_img_store, SqlAlchemyRepository


class UoW:
    def __init__(
        self,
        session_factory: sessionmaker = PSQL_SESSION_FACTORY,
        img_store_name: str = 'redis',
        store_details: Dict[str, str] = REDIS_CONNECTION
    ):
        self.session_factory = session_factory
        self.all_ingredients = None
        self.img_store_name = img_store_name
        self.store_details = store_details

    def __enter__(self) -> UoW:
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        self.img_store = create_img_store(self.img_store_name, self.store_details)
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
