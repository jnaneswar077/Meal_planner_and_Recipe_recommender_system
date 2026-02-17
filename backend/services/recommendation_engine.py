"""
Smart Meal Planner - Recommendation Engine
TF-IDF + Cosine Similarity based recipe recommendations
"""
import os
import ast
import re
import logging

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import CSV_PATH

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self):
        self.df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        self.is_ready = False

    def load_data(self):
        """Load and prepare recipe data from CSV."""
        if not os.path.exists(CSV_PATH):
            logger.error(f"CSV file not found: {CSV_PATH}")
            return False

        try:
            logger.info(f"Loading recipes from {CSV_PATH}...")
            self.df = pd.read_csv(CSV_PATH)
            logger.info(f"Loaded {len(self.df)} recipes")

            # Ensure required columns exist
            required = ["name", "description", "ingredients", "steps"]
            for col in required:
                if col not in self.df.columns:
                    logger.error(f"Missing required column: {col}")
                    return False

            # Fill NaN values
            for col in self.df.columns:
                if self.df[col].dtype == object:
                    self.df[col] = self.df[col].fillna("")

            # Create combined text feature for TF-IDF
            self.df["combined_text"] = (
                self.df["name"].astype(str) + " " +
                self.df["description"].astype(str) + " " +
                self.df["ingredients"].astype(str) + " " +
                self.df.get("tags", pd.Series([""] * len(self.df))).astype(str)
            )

            # Parse cooking time
            if "minutes" in self.df.columns:
                self.df["cooking_time"] = pd.to_numeric(self.df["minutes"], errors="coerce").fillna(30).astype(int)
            elif "cooking_time" in self.df.columns:
                self.df["cooking_time"] = pd.to_numeric(self.df["cooking_time"], errors="coerce").fillna(30).astype(int)
            else:
                self.df["cooking_time"] = 30

            # Parse n_steps and n_ingredients
            if "n_steps" not in self.df.columns:
                self.df["n_steps"] = self.df["steps"].apply(lambda x: len(self._parse_list(x)))
            if "n_ingredients" not in self.df.columns:
                self.df["n_ingredients"] = self.df["ingredients"].apply(lambda x: len(self._parse_list(x)))

            # Parse calories
            if "calories" not in self.df.columns and "nutrition" in self.df.columns:
                self.df["calories"] = self.df["nutrition"].apply(self._extract_calories)
            elif "calories" not in self.df.columns:
                self.df["calories"] = None

            # Assign difficulty based on cooking time and steps
            if "difficulty" not in self.df.columns:
                self.df["difficulty"] = self.df.apply(self._assign_difficulty, axis=1)

            # Build TF-IDF matrix
            logger.info("Building TF-IDF matrix...")
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df["combined_text"])
            logger.info("TF-IDF matrix built successfully")

            self.is_ready = True
            return True

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def _parse_list(self, value):
        """Parse a string representation of a list."""
        if isinstance(value, list):
            return value
        if not isinstance(value, str) or not value.strip():
            return []
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
        # Try splitting by comma
        return [item.strip() for item in value.split(",") if item.strip()]

    def _extract_calories(self, nutrition_str):
        """Extract calories from nutrition string."""
        try:
            if isinstance(nutrition_str, str):
                parsed = ast.literal_eval(nutrition_str)
                if isinstance(parsed, list) and len(parsed) > 0:
                    return float(parsed[0])
        except (ValueError, SyntaxError):
            pass
        return None

    def _assign_difficulty(self, row):
        """Assign difficulty based on cooking time and number of steps."""
        cooking_time = row.get("cooking_time", 30)
        n_steps = row.get("n_steps", 5)

        if cooking_time <= 20 and n_steps <= 5:
            return "Easy"
        elif cooking_time <= 45 and n_steps <= 10:
            return "Medium"
        else:
            return "Hard"

    def _extract_tags(self, row):
        """Extract dietary and cuisine tags from recipe data."""
        dietary_tags = []
        cuisine_tags = []

        tags_str = str(row.get("tags", ""))
        tags_list = self._parse_list(tags_str)

        dietary_keywords = ["vegetarian", "vegan", "gluten-free", "dairy-free",
                           "low-carb", "keto", "paleo", "healthy", "low-fat",
                           "sugar-free", "nut-free"]
        cuisine_keywords = ["italian", "mexican", "chinese", "indian", "japanese",
                           "thai", "french", "greek", "mediterranean", "korean",
                           "american", "british", "vietnamese", "middle-eastern"]

        for tag in tags_list:
            tag_lower = tag.lower().strip()
            if tag_lower in dietary_keywords:
                dietary_tags.append(tag_lower)
            elif tag_lower in cuisine_keywords:
                cuisine_tags.append(tag_lower)

        return dietary_tags, cuisine_tags

    def get_recommendations(self, query, n_recommendations=6, filters=None):
        """Get recipe recommendations based on query and optional filters."""
        if not self.is_ready:
            return []

        try:
            # Transform query using TF-IDF
            query_vec = self.vectorizer.transform([query])

            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            # Apply filters
            mask = np.ones(len(self.df), dtype=bool)

            if filters:
                if filters.get("max_cooking_time"):
                    mask &= self.df["cooking_time"] <= filters["max_cooking_time"]

                if filters.get("difficulty"):
                    mask &= self.df["difficulty"].str.lower() == filters["difficulty"].lower()

                if filters.get("dietary_restrictions"):
                    tags_col = self.df.get("tags", pd.Series([""] * len(self.df))).astype(str).str.lower()
                    for restriction in filters["dietary_restrictions"]:
                        mask &= tags_col.str.contains(restriction.lower(), na=False)

                if filters.get("cuisine"):
                    tags_col = self.df.get("tags", pd.Series([""] * len(self.df))).astype(str).str.lower()
                    mask &= tags_col.str.contains(filters["cuisine"].lower(), na=False)

            # Zero out filtered recipes
            filtered_similarities = similarities.copy()
            filtered_similarities[~mask] = 0

            # Get top N indices
            top_indices = filtered_similarities.argsort()[::-1][:n_recommendations]

            results = []
            for idx in top_indices:
                if filtered_similarities[idx] <= 0:
                    continue

                row = self.df.iloc[idx]
                dietary_tags, cuisine_tags = self._extract_tags(row)

                recipe = {
                    "id": int(idx),
                    "name": str(row.get("name", "Unknown")),
                    "description": str(row.get("description", ""))[:300],
                    "cooking_time": int(row.get("cooking_time", 30)),
                    "difficulty": str(row.get("difficulty", "Medium")),
                    "calories": float(row["calories"]) if pd.notna(row.get("calories")) else None,
                    "n_steps": int(row.get("n_steps", 0)),
                    "n_ingredients": int(row.get("n_ingredients", 0)),
                    "ingredients": self._parse_list(row.get("ingredients", "[]")),
                    "steps": self._parse_list(row.get("steps", "[]")),
                    "similarity_score": float(filtered_similarities[idx]),
                    "dietary_tags": dietary_tags,
                    "cuisine_tags": cuisine_tags,
                }
                results.append(recipe)

            return results

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def get_recipe_by_id(self, recipe_id):
        """Get a single recipe by its index ID."""
        if not self.is_ready or recipe_id < 0 or recipe_id >= len(self.df):
            return None

        row = self.df.iloc[recipe_id]
        dietary_tags, cuisine_tags = self._extract_tags(row)

        return {
            "id": int(recipe_id),
            "name": str(row.get("name", "Unknown")),
            "description": str(row.get("description", "")),
            "cooking_time": int(row.get("cooking_time", 30)),
            "difficulty": str(row.get("difficulty", "Medium")),
            "calories": float(row["calories"]) if pd.notna(row.get("calories")) else None,
            "n_steps": int(row.get("n_steps", 0)),
            "n_ingredients": int(row.get("n_ingredients", 0)),
            "ingredients": self._parse_list(row.get("ingredients", "[]")),
            "steps": self._parse_list(row.get("steps", "[]")),
            "similarity_score": None,
            "dietary_tags": dietary_tags,
            "cuisine_tags": cuisine_tags,
        }

    def quick_search(self, query, limit=6):
        """Quick text search by recipe name."""
        if not self.is_ready:
            return []

        query_lower = query.lower()
        matches = self.df[self.df["name"].str.lower().str.contains(query_lower, na=False)]

        results = []
        for idx, row in matches.head(limit).iterrows():
            dietary_tags, cuisine_tags = self._extract_tags(row)
            results.append({
                "id": int(idx) if isinstance(idx, (int, np.integer)) else int(self.df.index.get_loc(idx)),
                "name": str(row.get("name", "Unknown")),
                "description": str(row.get("description", ""))[:200],
                "cooking_time": int(row.get("cooking_time", 30)),
                "difficulty": str(row.get("difficulty", "Medium")),
                "calories": float(row["calories"]) if pd.notna(row.get("calories")) else None,
                "n_steps": int(row.get("n_steps", 0)),
                "n_ingredients": int(row.get("n_ingredients", 0)),
                "ingredients": self._parse_list(row.get("ingredients", "[]")),
                "steps": self._parse_list(row.get("steps", "[]")),
                "similarity_score": None,
                "dietary_tags": dietary_tags,
                "cuisine_tags": cuisine_tags,
            })

        return results


# Singleton instance
recommendation_engine = RecommendationEngine()
