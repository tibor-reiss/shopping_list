from __future__ import annotations  # Needed for __enter__
from sqlalchemy.orm import sessionmaker
from typing import Optional

from shopping_list.app.config import PSQL_SESSION_FACTORY
from shopping_list.app.repo import SqlAlchemyRepository


class UoW:
    def __init__(self, session_factory: sessionmaker = PSQL_SESSION_FACTORY):
        self.session_factory = session_factory
        self.ingredients = None
    
    def __enter__(self) -> UoW:
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        # Initialize only the first time the uow is used (and extend it with new ingredients in add_recipe)
        if self.ingredients is None:
            self.ingredients = self.repo.get_all_ingredients()
        return self
    
    def __exit__(self, *args):
        self.session.rollback()
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def append_ingredient(self, ing_name: str, unit: Optional[str] = None, category: Optional[str] = None):
        self.ingredients[ing_name] = {'unit': unit, 'category': category}
