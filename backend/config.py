"""
Smart Meal Planner - Configuration
"""
import os

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "smart-meal-planner-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "meal_planner.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Data
CSV_PATH = os.getenv(
    "CSV_PATH",
    r"C:\Users\jnane\Documents\temp\foodcom\cleaned_recipes.csv"
)
