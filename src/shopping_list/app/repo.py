import abc
from base64 import b64encode
from datetime import date
from io import BytesIO
import pymongo
from sqlalchemy import func
from sqlalchemy.orm import aliased
from typing import Any, Dict, List, Optional, Tuple, Union

from shopping_list.app.model import Ingredient, Meal, Recipe, RecipeIngredient


EXCLUDE_INGREDIENT = ['water', ]
EXCLUDE_CATEGORY = ['spice', ]


class SqlAlchemyRepository:
    def __init__(self, session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    def get(self, obj_type, attr_key, attr_value) -> Any:
        return self.session.query(obj_type).filter(getattr(obj_type, attr_key) == attr_value).one_or_none()

    def get_all(self, obj_type) -> List[Any]:
        return self.session.query(obj_type).all()

    def get_all_ingredients_as_dict(self) -> Dict[str, Dict[str, Union[int, str, None]]]:
        all_ingredients = {}
        for ing in self.session.query(Ingredient).all():
            all_ingredients[ing.ing_name] = {'unit': ing.unit, 'category': ing.category}
        return all_ingredients

    def get_all_recipe_ingredients(
        self,
        recipe_id: int
    ) -> List[Tuple[str, Optional[str], Optional[float], str]]:
        return (
            self.session.query(
                Ingredient.ing_name,
                Ingredient.unit,
                RecipeIngredient.amount,
                Ingredient.category
            )
            .filter(RecipeIngredient.recipe_id == recipe_id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .order_by(Ingredient.ing_name)
            .all()
        )

    def get_total_ingredients(
        self,
        start_date: date,
        end_date: date,
        column_name: str
    ) -> List[Tuple[str, float, str]]:
        t_i = aliased(Ingredient)
        t_r = aliased(Recipe)
        t_ri = aliased(RecipeIngredient)
        t_m = aliased(Meal)
        # The big query is needed because e.g. the same recipe can be multiple times as lunch/dinner
        return (
            self.session.query(
                t_i.ing_name.label('ingredient'),
                func.sum(t_ri.amount).label('total'),
                t_i.unit
            )
            .join(t_ri, t_ri.ingredient_id == t_i.id)
            .join(t_r, t_ri.recipe_id == t_r.id)
            .join(t_m, getattr(t_m, column_name) == t_r.title)
            .filter(t_m.date >= start_date).filter(t_m.date <= end_date)
            .filter(t_ri.amount > 0)
            .filter(t_i.ing_name.notin_(EXCLUDE_INGREDIENT))
            .filter(t_i.category.notin_(EXCLUDE_CATEGORY))
            .group_by(t_i.ing_name)
            .group_by(t_i.unit)
            .group_by(t_i.category)
            .order_by(t_i.category)
            .all()
        )


class ImageStore(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get(self, img_id: int):
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, img: Any, img_id: int):
        raise NotImplementedError
    
    @abc.abstractmethod
    def close(self):
        raise NotImplementedError


class MongoStore(ImageStore):
    def __init__(self, config_dict: Dict[str, str]):
        super().__init__()
        self.mongo_client = pymongo.MongoClient(config_dict['uri'])
        self.mongo_db = config_dict['db']
        self.mongo_collection = config_dict['coll']

    def get_mongo_collection(self):
        return self.mongo_client[self.mongo_db][self.mongo_collection]

    def get(self, img_id: int) -> Optional[str]:
        result = self.get_mongo_collection().find_one({'img_id': img_id})
        if result is None:
            return None
        img = BytesIO(result['img'])
        return b64encode(img.getvalue()).decode('utf-8')

    def add(self, img: Any, img_id: int):
        img.seek(0)
        image_file = BytesIO(img.read())
        self.get_mongo_collection().update_one(
            {'img_id': img_id},
            {"$set": {'img_id': img_id, 'img': image_file.getvalue()}},
            upsert=True
        )

    def close(self):
        self.mongo_client.close()
