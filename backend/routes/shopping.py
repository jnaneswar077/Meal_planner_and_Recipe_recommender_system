"""
Smart Meal Planner - Shopping List Routes
"""
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db, User, MealPlan, MealPlanItem, ShoppingList, ShoppingListItem
from schemas import (
    ShoppingListGenerate, ShoppingListResponse, ShoppingListItemResponse,
    ShoppingListItemUpdate
)
from utils.auth import get_current_user
from services.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/shopping-lists", tags=["Shopping Lists"])


# Category mapping for common ingredients
CATEGORY_MAP = {
    "chicken": "meat", "beef": "meat", "pork": "meat", "lamb": "meat",
    "turkey": "meat", "bacon": "meat", "sausage": "meat", "ham": "meat",
    "steak": "meat", "ground": "meat",
    "salmon": "seafood", "shrimp": "seafood", "fish": "seafood",
    "tuna": "seafood", "crab": "seafood", "lobster": "seafood",
    "milk": "dairy", "cheese": "dairy", "butter": "dairy", "cream": "dairy",
    "yogurt": "dairy", "egg": "dairy", "sour cream": "dairy",
    "lettuce": "vegetables", "tomato": "vegetables", "onion": "vegetables",
    "garlic": "vegetables", "pepper": "vegetables", "carrot": "vegetables",
    "celery": "vegetables", "broccoli": "vegetables", "spinach": "vegetables",
    "mushroom": "vegetables", "potato": "vegetables", "corn": "vegetables",
    "zucchini": "vegetables", "cucumber": "vegetables", "cabbage": "vegetables",
    "bean": "vegetables", "pea": "vegetables", "asparagus": "vegetables",
    "eggplant": "vegetables", "cauliflower": "vegetables",
    "apple": "fruits", "banana": "fruits", "lemon": "fruits", "lime": "fruits",
    "orange": "fruits", "berry": "fruits", "strawberry": "fruits",
    "blueberry": "fruits", "avocado": "fruits", "mango": "fruits",
    "rice": "grains", "pasta": "grains", "bread": "grains", "flour": "grains",
    "noodle": "grains", "oat": "grains", "tortilla": "grains",
    "cereal": "grains", "quinoa": "grains", "couscous": "grains",
    "salt": "herbs_spices", "pepper": "herbs_spices", "basil": "herbs_spices",
    "oregano": "herbs_spices", "thyme": "herbs_spices", "rosemary": "herbs_spices",
    "cumin": "herbs_spices", "paprika": "herbs_spices", "cinnamon": "herbs_spices",
    "parsley": "herbs_spices", "cilantro": "herbs_spices", "dill": "herbs_spices",
    "ginger": "herbs_spices", "nutmeg": "herbs_spices", "chili": "herbs_spices",
    "oil": "pantry", "vinegar": "pantry", "sauce": "pantry", "sugar": "pantry",
    "honey": "pantry", "syrup": "pantry", "broth": "pantry", "stock": "pantry",
    "ketchup": "pantry", "mustard": "pantry", "mayonnaise": "pantry",
    "soy sauce": "pantry", "can": "pantry", "tomato sauce": "pantry",
}


def _categorize_ingredient(ingredient_name: str) -> str:
    """Categorize an ingredient into a food category."""
    lower = ingredient_name.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in lower:
            return category
    return "other"


def _plan_to_shopping_response(shopping_list: ShoppingList) -> ShoppingListResponse:
    """Convert a ShoppingList ORM object to response."""
    items = [
        ShoppingListItemResponse(
            item_id=item.item_id,
            ingredient_name=item.ingredient_name,
            quantity=item.quantity,
            unit=item.unit,
            category=item.category,
            is_checked=item.is_checked,
        )
        for item in shopping_list.items
    ]
    return ShoppingListResponse(
        list_id=shopping_list.list_id,
        user_id=shopping_list.user_id,
        plan_id=shopping_list.plan_id,
        items=items,
        total_items=len(items),
    )


@router.post("/generate", response_model=ShoppingListResponse)
def generate_shopping_list(
    data: ShoppingListGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a shopping list from a meal plan."""
    # Verify meal plan exists and belongs to user
    plan = (
        db.query(MealPlan)
        .filter(
            MealPlan.plan_id == data.plan_id,
            MealPlan.user_id == current_user.user_id,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    if not plan.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meal plan has no meals. Add some recipes first.",
        )

    # Delete existing shopping list for this plan
    existing = (
        db.query(ShoppingList)
        .filter(
            ShoppingList.plan_id == data.plan_id,
            ShoppingList.user_id == current_user.user_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()

    # Collect all ingredients from meal plan recipes
    ingredient_map = {}  # name -> {quantity, unit, category}

    for meal_item in plan.items:
        recipe = recommendation_engine.get_recipe_by_id(meal_item.recipe_id)
        if not recipe:
            continue

        for ingredient_str in recipe.get("ingredients", []):
            # Clean and normalize ingredient name
            clean_name = ingredient_str.strip().lower()
            if not clean_name:
                continue

            if clean_name in ingredient_map:
                ingredient_map[clean_name]["quantity"] += 1
            else:
                ingredient_map[clean_name] = {
                    "quantity": 1,
                    "unit": "item",
                    "category": _categorize_ingredient(clean_name),
                }

    # Create shopping list
    shopping_list = ShoppingList(
        user_id=current_user.user_id,
        plan_id=data.plan_id,
    )
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)

    # Add items
    for name, info in ingredient_map.items():
        item = ShoppingListItem(
            list_id=shopping_list.list_id,
            ingredient_name=name,
            quantity=info["quantity"],
            unit=info["unit"],
            category=info["category"],
            is_checked=False,
        )
        db.add(item)

    db.commit()
    db.refresh(shopping_list)

    return _plan_to_shopping_response(shopping_list)


@router.get("/", response_model=list)
def list_shopping_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all shopping lists for the current user."""
    lists = (
        db.query(ShoppingList)
        .filter(ShoppingList.user_id == current_user.user_id)
        .order_by(ShoppingList.created_at.desc())
        .all()
    )
    return [_plan_to_shopping_response(sl) for sl in lists]


@router.get("/{list_id}", response_model=ShoppingListResponse)
def get_shopping_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific shopping list."""
    shopping_list = (
        db.query(ShoppingList)
        .filter(
            ShoppingList.list_id == list_id,
            ShoppingList.user_id == current_user.user_id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    return _plan_to_shopping_response(shopping_list)


@router.patch("/{list_id}/items/{item_id}", response_model=ShoppingListItemResponse)
def toggle_item(
    list_id: int,
    item_id: int,
    update: ShoppingListItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle a shopping list item's checked status."""
    # Verify list belongs to user
    shopping_list = (
        db.query(ShoppingList)
        .filter(
            ShoppingList.list_id == list_id,
            ShoppingList.user_id == current_user.user_id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    item = (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.item_id == item_id,
            ShoppingListItem.list_id == list_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    item.is_checked = update.is_checked
    db.commit()
    db.refresh(item)

    return ShoppingListItemResponse(
        item_id=item.item_id,
        ingredient_name=item.ingredient_name,
        quantity=item.quantity,
        unit=item.unit,
        category=item.category,
        is_checked=item.is_checked,
    )


@router.delete("/{list_id}/items/{item_id}")
def delete_item(
    list_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a shopping list item."""
    # Verify list belongs to user
    shopping_list = (
        db.query(ShoppingList)
        .filter(
            ShoppingList.list_id == list_id,
            ShoppingList.user_id == current_user.user_id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found",
        )

    item = (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.item_id == item_id,
            ShoppingListItem.list_id == list_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    db.delete(item)
    db.commit()

    return {"message": "Item deleted successfully"}
