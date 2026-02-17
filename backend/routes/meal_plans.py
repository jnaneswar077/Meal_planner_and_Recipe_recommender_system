"""
Smart Meal Planner - Meal Plan Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db, User, MealPlan, MealPlanItem
from schemas import (
    MealPlanCreate, MealPlanItemAdd, MealPlanResponse, MealPlanItemResponse
)
from utils.auth import get_current_user
from services.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])


def _plan_to_response(plan: MealPlan) -> MealPlanResponse:
    """Convert a MealPlan ORM object to a response model."""
    meals = [
        MealPlanItemResponse(
            item_id=item.item_id,
            recipe_id=item.recipe_id,
            recipe_name=item.recipe_name,
            day_of_week=item.day_of_week,
            meal_type=item.meal_type,
            date=item.date,
            cooking_time=item.cooking_time,
        )
        for item in plan.items
    ]
    return MealPlanResponse(
        plan_id=plan.plan_id,
        user_id=plan.user_id,
        week_start_date=plan.week_start_date,
        week_end_date=plan.week_end_date,
        meals=meals,
    )


@router.post("/create", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def create_meal_plan(
    plan_data: MealPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new meal plan or return existing one for the given week."""
    # Check if a plan already exists for this week
    existing = (
        db.query(MealPlan)
        .filter(
            MealPlan.user_id == current_user.user_id,
            MealPlan.week_start_date == plan_data.week_start_date,
            MealPlan.week_end_date == plan_data.week_end_date,
        )
        .first()
    )

    if existing:
        return _plan_to_response(existing)

    # Create new plan
    new_plan = MealPlan(
        user_id=current_user.user_id,
        week_start_date=plan_data.week_start_date,
        week_end_date=plan_data.week_end_date,
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return _plan_to_response(new_plan)


@router.get("/current", response_model=MealPlanResponse)
def get_current_week_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current week's meal plan."""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    week_start = monday.strftime("%Y-%m-%d")
    week_end = sunday.strftime("%Y-%m-%d")

    plan = (
        db.query(MealPlan)
        .filter(
            MealPlan.user_id == current_user.user_id,
            MealPlan.week_start_date == week_start,
        )
        .first()
    )

    if not plan:
        # Auto-create plan for current week
        plan = MealPlan(
            user_id=current_user.user_id,
            week_start_date=week_start,
            week_end_date=week_end,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

    return _plan_to_response(plan)


@router.get("/", response_model=list)
def list_meal_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all meal plans for the current user."""
    plans = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.user_id)
        .order_by(MealPlan.week_start_date.desc())
        .all()
    )
    return [_plan_to_response(plan) for plan in plans]


@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_meal_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific meal plan."""
    plan = (
        db.query(MealPlan)
        .filter(
            MealPlan.plan_id == plan_id,
            MealPlan.user_id == current_user.user_id,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    return _plan_to_response(plan)


@router.post("/{plan_id}/add-meal", response_model=MealPlanItemResponse)
def add_meal(
    plan_id: int,
    meal_data: MealPlanItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a recipe to a meal plan slot."""
    # Verify plan belongs to user
    plan = (
        db.query(MealPlan)
        .filter(
            MealPlan.plan_id == plan_id,
            MealPlan.user_id == current_user.user_id,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    # Get recipe details from recommendation engine
    recipe = recommendation_engine.get_recipe_by_id(meal_data.recipe_id)
    recipe_name = recipe["name"] if recipe else f"Recipe #{meal_data.recipe_id}"
    cooking_time = recipe["cooking_time"] if recipe else 30

    # Check if slot is already occupied, if so replace
    existing_item = (
        db.query(MealPlanItem)
        .filter(
            MealPlanItem.plan_id == plan_id,
            MealPlanItem.day_of_week == meal_data.day_of_week,
            MealPlanItem.meal_type == meal_data.meal_type,
        )
        .first()
    )

    if existing_item:
        existing_item.recipe_id = meal_data.recipe_id
        existing_item.recipe_name = recipe_name
        existing_item.cooking_time = cooking_time
        existing_item.date = meal_data.date
        db.commit()
        db.refresh(existing_item)
        return MealPlanItemResponse(
            item_id=existing_item.item_id,
            recipe_id=existing_item.recipe_id,
            recipe_name=existing_item.recipe_name,
            day_of_week=existing_item.day_of_week,
            meal_type=existing_item.meal_type,
            date=existing_item.date,
            cooking_time=existing_item.cooking_time,
        )

    # Create new meal plan item
    new_item = MealPlanItem(
        plan_id=plan_id,
        recipe_id=meal_data.recipe_id,
        recipe_name=recipe_name,
        day_of_week=meal_data.day_of_week,
        meal_type=meal_data.meal_type,
        date=meal_data.date,
        cooking_time=cooking_time,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return MealPlanItemResponse(
        item_id=new_item.item_id,
        recipe_id=new_item.recipe_id,
        recipe_name=new_item.recipe_name,
        day_of_week=new_item.day_of_week,
        meal_type=new_item.meal_type,
        date=new_item.date,
        cooking_time=new_item.cooking_time,
    )


@router.delete("/{plan_id}/items/{item_id}")
def remove_meal(
    plan_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a meal from the plan."""
    # Verify plan belongs to user
    plan = (
        db.query(MealPlan)
        .filter(
            MealPlan.plan_id == plan_id,
            MealPlan.user_id == current_user.user_id,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    item = (
        db.query(MealPlanItem)
        .filter(
            MealPlanItem.item_id == item_id,
            MealPlanItem.plan_id == plan_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan item not found",
        )

    db.delete(item)
    db.commit()

    return {"message": "Meal removed successfully"}
