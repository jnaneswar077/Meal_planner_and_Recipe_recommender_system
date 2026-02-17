"""
Smart Meal Planner - Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ================================
# AUTH SCHEMAS
# ================================

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user_id: int
    username: str
    token: str


# ================================
# RECIPE SCHEMAS
# ================================

class RecommendRequest(BaseModel):
    query: str
    n_recommendations: int = 6
    dietary_restrictions: Optional[List[str]] = None
    max_cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str
    cooking_time: int
    difficulty: str
    calories: Optional[float] = None
    n_steps: int
    n_ingredients: int
    ingredients: List[str]
    steps: List[str]
    similarity_score: Optional[float] = None
    dietary_tags: Optional[List[str]] = None
    cuisine_tags: Optional[List[str]] = None


class RecommendResponse(BaseModel):
    recommendations: List[RecipeResponse]
    query: str
    total: int


# ================================
# MEAL PLAN SCHEMAS
# ================================

class MealPlanCreate(BaseModel):
    week_start_date: str
    week_end_date: str


class MealPlanItemAdd(BaseModel):
    recipe_id: int
    day_of_week: str
    meal_type: str
    date: Optional[str] = None


class MealPlanItemResponse(BaseModel):
    item_id: int
    recipe_id: int
    recipe_name: str
    day_of_week: str
    meal_type: str
    date: Optional[str] = None
    cooking_time: Optional[int] = None

    class Config:
        from_attributes = True


class MealPlanResponse(BaseModel):
    plan_id: int
    user_id: int
    week_start_date: str
    week_end_date: str
    meals: List[MealPlanItemResponse] = []

    class Config:
        from_attributes = True


# ================================
# SHOPPING LIST SCHEMAS
# ================================

class ShoppingListGenerate(BaseModel):
    plan_id: int


class ShoppingListItemResponse(BaseModel):
    item_id: int
    ingredient_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    is_checked: bool = False

    class Config:
        from_attributes = True


class ShoppingListItemUpdate(BaseModel):
    is_checked: bool


class ShoppingListResponse(BaseModel):
    list_id: int
    user_id: int
    plan_id: int
    items: List[ShoppingListItemResponse] = []
    total_items: int = 0

    class Config:
        from_attributes = True
