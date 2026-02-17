"""
Smart Meal Planner - Recipe Routes
"""
from fastapi import APIRouter, HTTPException, Query, status

from schemas import RecommendRequest, RecommendResponse, RecipeResponse
from services.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.post("/recommend", response_model=RecommendResponse)
def get_recommendations(request: RecommendRequest):
    """Get recipe recommendations based on query and filters."""
    if not recommendation_engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recipe data is not available. Please ensure the backend has loaded the data.",
        )

    filters = {}
    if request.dietary_restrictions:
        filters["dietary_restrictions"] = request.dietary_restrictions
    if request.max_cooking_time:
        filters["max_cooking_time"] = request.max_cooking_time
    if request.difficulty:
        filters["difficulty"] = request.difficulty
    if request.cuisine:
        filters["cuisine"] = request.cuisine

    recommendations = recommendation_engine.get_recommendations(
        query=request.query,
        n_recommendations=request.n_recommendations,
        filters=filters if filters else None,
    )

    return RecommendResponse(
        recommendations=[RecipeResponse(**r) for r in recommendations],
        query=request.query,
        total=len(recommendations),
    )


@router.get("/search/quick")
def quick_search(q: str = Query(..., min_length=1), limit: int = Query(6, ge=1, le=20)):
    """Quick search recipes by name."""
    if not recommendation_engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recipe data is not available.",
        )

    results = recommendation_engine.quick_search(q, limit=limit)
    return results


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int):
    """Get a recipe by ID."""
    if not recommendation_engine.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recipe data is not available.",
        )

    recipe = recommendation_engine.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return RecipeResponse(**recipe)
