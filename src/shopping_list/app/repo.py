
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import aliased
from typing import Optional, List, Tuple

from shopping_list.app.model import Ingredient, Meal, Recipe, RecipeIngredient


class SqlAlchemyRepository:
    def __init__(self, session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)
    
    def get(self, obj_type, attr_key, attr_value):
        return self.session.query(obj_type).filter(getattr(obj_type, attr_key) == attr_value).one_or_none()
    
    def get_all(self, obj_type):
        return self.session.query(obj_type).all()

    def get_all_recipe_ingredients(self, recipe_id: int) -> List[Tuple[str, str, float]]:
        return self.session.query(
                Ingredient.ing_name.label('ing_name'), Ingredient.unit, RecipeIngredient.amount
            ).filter(RecipeIngredient.recipe_id == recipe_id
            ).join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id
            ).all()

    def get_one_recipe_ingredient(self, recipe_id: int, ingredient_id: int) -> Optional[RecipeIngredient]:
        return self.session.query(RecipeIngredient
            ).filter(RecipeIngredient.recipe_id == recipe_id
            ).filter(RecipeIngredient.ingredient_id == ingredient_id
            ).one_or_none()

    def get_total_ingredients(self, start_date: date, end_date: date, column_name: str) -> List:
        t_i = aliased(Ingredient)
        t_r = aliased(Recipe)
        t_ri = aliased(RecipeIngredient)
        t_m = aliased(Meal)
        # The big query is needed because e.g. the same recipe can be multiple times as lunch/dinner
        return self.session.query(
                t_i.ing_name.label('ingredient'), func.sum(t_ri.amount).label('total'), t_i.unit
            ).join(t_ri, t_ri.ingredient_id == t_i.id
            ).join(t_r, t_ri.recipe_id == t_r.id
            ).join(t_m, getattr(t_m, column_name) == t_r.title
            ).filter(t_m.date >= start_date).filter(t_m.date <= end_date
            ).filter(t_ri.amount > 0
            ).group_by(t_i.ing_name
            ).group_by(t_i.unit).all()
