"""
Smart Meal Planner - Database Models & Connection
"""
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime,
    Boolean, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ================================
# Models
# ================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    dietary_restrictions = Column(String(255))
    favorite_cuisines = Column(String(255))
    disliked_ingredients = Column(Text)
    cooking_skill = Column(String(50))

    user = relationship("User", back_populates="preferences")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    week_start_date = Column(String(20), nullable=False)
    week_end_date = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_plans")
    items = relationship("MealPlanItem", back_populates="meal_plan", cascade="all, delete-orphan")


class MealPlanItem(Base):
    __tablename__ = "meal_plan_items"

    item_id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("meal_plans.plan_id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, nullable=False)
    recipe_name = Column(String(200), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    meal_type = Column(String(20), nullable=False)
    date = Column(String(20))
    cooking_time = Column(Integer)

    meal_plan = relationship("MealPlan", back_populates="items")


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    list_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("meal_plans.plan_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    item_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.list_id", ondelete="CASCADE"), nullable=False)
    ingredient_name = Column(String(200), nullable=False)
    quantity = Column(Float)
    unit = Column(String(50))
    category = Column(String(100))
    is_checked = Column(Boolean, default=False)

    shopping_list = relationship("ShoppingList", back_populates="items")


# ================================
# Database Dependency
# ================================

def get_db():
    """FastAPI dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
