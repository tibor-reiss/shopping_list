from datetime import date as dt
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import backref, relationship
from typing import Optional


Base = declarative_base()


class Ingredient(Base):
    __tablename__ = 'shlist.ingredient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ing_name = Column(String(32), unique=True)
    unit = Column(String(10))

    def __init__(self, ing_name: str, unit: Optional[str] = None):
        self.ing_name = ing_name
        self.unit = unit


class Recipe(Base):
    __tablename__ = 'shlist.recipe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    ingredients = association_proxy('recipe_ingredients', 'ingredient')

    def __init__(self, title: str, description: Optional[str] = None):
        self.title = title
        self.description = description


class RecipeIngredient(Base):
    __tablename__ = 'shlist.recipe_ingredient'
    recipe_id = Column(Integer, ForeignKey('shlist.recipe.id', ondelete='CASCADE'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('shlist.ingredient.id', ondelete='CASCADE'), primary_key=True)
    amount = Column(Float)

    recipe = relationship(Recipe, backref=backref('recipe_ingredients', cascade='all, delete-orphan'))
    ingredient = relationship('Ingredient')

    def __init__(self, ingredient=None, recipe=None, amount=None):
        self.recipe = recipe
        self.ingredient = ingredient
        self.amount = amount


class Meal(Base):
    __tablename__ = 'shlist.meal'
    date = Column(Date, primary_key=True)
    _lunch = Column('lunch', String(128), ForeignKey('shlist.recipe.title', ondelete='SET NULL', onupdate='CASCADE'))
    _dinner = Column('dinner', String(128), ForeignKey('shlist.recipe.title', ondelete='SET NULL', onupdate='CASCADE'))

    def __init__(self, date: dt, lunch: Optional[str] = None, dinner: Optional[str] = None):
        self.date = date
        self.lunch = lunch
        self.dinner = dinner
    
    @hybrid_property
    def lunch(self):
        return self._lunch
    
    @lunch.setter
    def lunch(self, value):
        self._lunch = value if value else None  # Need to handle empty string the same way as None

    @hybrid_property
    def dinner(self):
        return self._dinner
    
    @dinner.setter
    def dinner(self, value):
        self._dinner = value if value else None  # Need to handle empty string the same way as None
