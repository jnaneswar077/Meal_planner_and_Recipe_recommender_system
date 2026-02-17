"""
Smart Meal Planner - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from services.recommendation_engine import recommendation_engine
from routes import auth, recipes, meal_plans, shopping

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Smart Meal Planner API...")

    # Initialize database tables
    init_db()
    logger.info("✅ Database initialized")

    # Load recommendation engine data
    logger.info("📊 Loading recipe data (this may take 30-60 seconds on first run)...")
    success = recommendation_engine.load_data()
    if success:
        logger.info(f"✅ Recommendation engine ready with {len(recommendation_engine.df)} recipes")
    else:
        logger.warning("⚠️ Recommendation engine failed to load. Recipe features will be unavailable.")

    yield

    # Shutdown
    logger.info("👋 Shutting down Smart Meal Planner API")


# Create FastAPI app
app = FastAPI(
    title="Smart Meal Planner API",
    description="AI-powered meal planning with recipe recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(meal_plans.router, prefix="/api")
app.include_router(shopping.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "status": "running",
        "app": "Smart Meal Planner API",
        "version": "1.0.0",
        "recommendation_engine": recommendation_engine.is_ready,
    }
