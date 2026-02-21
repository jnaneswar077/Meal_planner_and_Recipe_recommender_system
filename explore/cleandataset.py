"""
Food.com Dataset Cleaning Script
Cleans and prepares the RAW recipe data for the recommendation engine
"""

import pandas as pd
import ast
import numpy as np

# Configuration
RAW_DATASET_PATH = r'C:\Users\jnane\Documents\temp\foodcom\RAW_recipes.csv'
CLEANED_DATASET_PATH = r'C:\Users\jnane\Documents\temp\foodcom\cleaned_recipes.csv'

def clean_recipes_dataset():
    """Clean and prepare the recipes dataset"""
    
    print("="*80)
    print("FOOD.COM DATASET CLEANING")
    print("="*80)
    
    # Load dataset
    print("\n📂 Loading RAW dataset...")
    df = pd.read_csv(RAW_DATASET_PATH)
    initial_count = len(df)
    print(f"✅ Loaded {initial_count:,} recipes")
    
    # Step 1: Remove recipes with missing names
    print("\n" + "="*80)
    print("STEP 1: Removing recipes with missing names")
    print("="*80)
    before = len(df)
    df = df.dropna(subset=['name'])
    after = len(df)
    print(f"Removed {before - after} recipes with missing names")
    print(f"Remaining: {after:,} recipes")
    
    # Step 2: Remove duplicate recipes (based on name)
    print("\n" + "="*80)
    print("STEP 2: Removing duplicate recipes")
    print("="*80)
    before = len(df)
    df = df.drop_duplicates(subset=['name'], keep='first')
    after = len(df)
    print(f"Removed {before - after} duplicate recipes")
    print(f"Remaining: {after:,} recipes")
    
    # Step 3: Filter by cooking time (remove outliers)
    print("\n" + "="*80)
    print("STEP 3: Filtering by reasonable cooking time")
    print("="*80)
    before = len(df)
    # Keep recipes between 1 minute and 480 minutes (8 hours)
    df = df[(df['minutes'] >= 1) & (df['minutes'] <= 120)]
    after = len(df)
    print(f"Removed {before - after} recipes with unrealistic cooking times")
    print(f"Kept recipes: 1 to 120 minutes (2 hours)")
    print(f"Remaining: {after:,} recipes")
    
    # Step 4: Filter by number of steps
    print("\n" + "="*80)
    print("STEP 4: Filtering by number of steps")
    print("="*80)
    before = len(df)
    # Keep recipes with 1 to 50 steps
    df = df[(df['n_steps'] >= 1) & (df['n_steps'] <= 50)]
    after = len(df)
    print(f"Removed {before - after} recipes with 0 or too many steps")
    print(f"Kept recipes: 1 to 50 steps")
    print(f"Remaining: {after:,} recipes")
    
    # Step 5: Filter by number of ingredients
    print("\n" + "="*80)
    print("STEP 5: Filtering by number of ingredients")
    print("="*80)
    before = len(df)
    # Keep recipes with 1 to 30 ingredients
    df = df[(df['n_ingredients'] >= 1) & (df['n_ingredients'] <= 30)]
    after = len(df)
    print(f"Removed {before - after} recipes with unusual ingredient counts")
    print(f"Kept recipes: 1 to 30 ingredients")
    print(f"Remaining: {after:,} recipes")
    
    # Step 6: Handle missing descriptions
    print("\n" + "="*80)
    print("STEP 6: Handling missing descriptions")
    print("="*80)
    missing_desc = df['description'].isna().sum()
    print(f"Found {missing_desc} recipes with missing descriptions")
    # Fill missing descriptions with recipe name + ingredients
    df['description'] = df.apply(
        lambda row: row['description'] if pd.notna(row['description']) 
        else f"{row['name']}. Made with {row['ingredients'][:50]}",
        axis=1
    )
    print(f"✅ Filled missing descriptions with recipe name and ingredients")
    
    # Step 7: Clean and standardize text fields
    print("\n" + "="*80)
    print("STEP 7: Cleaning text fields")
    print("="*80)
    
    # Clean recipe names (lowercase, strip whitespace)
    df['name'] = df['name'].str.lower().str.strip()
    
    # Clean descriptions
    df['description'] = df['description'].str.strip()
    
    print("✅ Cleaned recipe names and descriptions")
    
    # Step 8: Parse list-like columns
    print("\n" + "="*80)
    print("STEP 8: Parsing list columns")
    print("="*80)
    
    def safe_parse_list(x):
        """Safely parse string representation of list"""
        try:
            if isinstance(x, str):
                return ast.literal_eval(x)
            return x
        except:
            return []
    
    # Parse ingredients, steps, tags, nutrition
    df['ingredients'] = df['ingredients'].apply(safe_parse_list)
    df['steps'] = df['steps'].apply(safe_parse_list)
    df['tags'] = df['tags'].apply(safe_parse_list)
    df['nutrition'] = df['nutrition'].apply(safe_parse_list)
    
    print("✅ Parsed list columns (ingredients, steps, tags, nutrition)")
    
    # Step 9: Create combined text field for TF-IDF
    print("\n" + "="*80)
    print("STEP 9: Creating combined text field for recommendation engine")
    print("="*80)
    
    def create_combined_text(row):
        """Combine all relevant text fields for TF-IDF vectorization"""
        # Recipe name
        name = row['name']
        
        # Description
        desc = row['description'] if pd.notna(row['description']) else ''
        
        # Ingredients (join list)
        ingredients = ' '.join(row['ingredients']) if isinstance(row['ingredients'], list) else ''
        
        # Tags (join first 10)
        tags = ' '.join(row['tags']) if isinstance(row['tags'], list) else ''
        
        # Combine all
        combined = f"{name} {desc} {ingredients} {tags}"
        return combined.lower()
    
    df['combined_text'] = df.apply(create_combined_text, axis=1)
    print("✅ Created 'combined_text' field for recommendations")
    
    # Step 10: Extract useful tag categories
    print("\n" + "="*80)
    print("STEP 10: Extracting dietary and cuisine tags")
    print("="*80)
    
    # Common dietary tags
    dietary_tags_list = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 
                        'low-carb', 'low-fat', 'low-calorie', 'high-protein',
                        'diabetic', 'healthy', 'low-sodium']
    
    # Common cuisine tags
    cuisine_tags_list = ['italian', 'mexican', 'chinese', 'indian', 'thai',
                        'japanese', 'french', 'american', 'greek', 'spanish',
                        'mediterranean', 'middle-eastern', 'asian']
    
    # Meal type tags
    meal_type_tags = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert',
                     'appetizer', 'main-dish', 'side-dishes']
    
    def extract_tag_categories(tags):
        """Extract dietary, cuisine, and meal type tags"""
        if not isinstance(tags, list):
            return {'dietary': [], 'cuisine': [], 'meal_type': []}
        
        tags_lower = [tag.lower() for tag in tags]
        
        dietary = [tag for tag in dietary_tags_list if tag in tags_lower]
        cuisine = [tag for tag in cuisine_tags_list if tag in tags_lower]
        meal_type = [tag for tag in meal_type_tags if tag in tags_lower]
        
        return {
            'dietary': dietary,
            'cuisine': cuisine,
            'meal_type': meal_type
        }
    
    df['tag_categories'] = df['tags'].apply(extract_tag_categories)
    df['dietary_tags'] = df['tag_categories'].apply(lambda x: x['dietary'])
    df['cuisine_tags'] = df['tag_categories'].apply(lambda x: x['cuisine'])
    df['meal_type_tags'] = df['tag_categories'].apply(lambda x: x['meal_type'])
    
    print("✅ Extracted dietary, cuisine, and meal type tags")
    
    # Step 11: Add difficulty level based on steps and time
    print("\n" + "="*80)
    print("STEP 11: Calculating difficulty level")
    print("="*80)
    
    def calculate_difficulty(row):
        """Calculate difficulty based on steps and cooking time"""
        steps = row['n_steps']
        minutes = row['minutes']
        
        # Simple scoring system
        if steps <= 5 and minutes <= 30:
            return 'easy'
        elif steps <= 10 and minutes <= 60:
            return 'medium'
        else:
            return 'hard'
    
    df['difficulty'] = df.apply(calculate_difficulty, axis=1)
    
    difficulty_counts = df['difficulty'].value_counts()
    print(f"Difficulty distribution:")
    for level, count in difficulty_counts.items():
        print(f"  {level.capitalize()}: {count:,} recipes")
    
    # Step 12: Extract nutrition values
    print("\n" + "="*80)
    print("STEP 12: Extracting nutrition values")
    print("="*80)
    
    def extract_nutrition(nutrition_list):
        """Extract individual nutrition values"""
        if not isinstance(nutrition_list, list) or len(nutrition_list) < 7:
            return {
                'calories': None,
                'total_fat': None,
                'sugar': None,
                'sodium': None,
                'protein': None,
                'saturated_fat': None,
                'carbohydrates': None
            }
        
        return {
            'calories': nutrition_list[0],
            'total_fat': nutrition_list[1],
            'sugar': nutrition_list[2],
            'sodium': nutrition_list[3],
            'protein': nutrition_list[4],
            'saturated_fat': nutrition_list[5],
            'carbohydrates': nutrition_list[6]
        }
    
    nutrition_df = df['nutrition'].apply(extract_nutrition).apply(pd.Series)
    df = pd.concat([df, nutrition_df], axis=1)
    
    print("✅ Extracted nutrition values into separate columns")
    
    # Final statistics
    print("\n" + "="*80)
    print("CLEANING SUMMARY")
    print("="*80)
    final_count = len(df)
    removed_count = initial_count - final_count
    removed_pct = (removed_count / initial_count) * 100
    
    print(f"Initial recipes:    {initial_count:,}")
    print(f"Final recipes:      {final_count:,}")
    print(f"Removed:            {removed_count:,} ({removed_pct:.2f}%)")
    print(f"Retention rate:     {(final_count/initial_count)*100:.2f}%")
    
    print("\n📊 Final Dataset Statistics:")
    print(f"  Cooking time:     {df['minutes'].min()}-{df['minutes'].max()} minutes")
    print(f"  Avg cooking time: {df['minutes'].mean():.1f} minutes")
    print(f"  Ingredients:      {df['n_ingredients'].min()}-{df['n_ingredients'].max()}")
    print(f"  Avg ingredients:  {df['n_ingredients'].mean():.1f}")
    print(f"  Steps:            {df['n_steps'].min()}-{df['n_steps'].max()}")
    print(f"  Avg steps:        {df['n_steps'].mean():.1f}")
    
    # Save cleaned dataset
    print("\n" + "="*80)
    print("SAVING CLEANED DATASET")
    print("="*80)
    
    # Select important columns for the cleaned dataset
    columns_to_keep = [
        'id', 'name', 'description', 'minutes', 'n_steps', 'n_ingredients',
        'ingredients', 'steps', 'tags', 'combined_text',
        'dietary_tags', 'cuisine_tags', 'meal_type_tags', 'difficulty',
        'calories', 'total_fat', 'sugar', 'sodium', 'protein',
        'saturated_fat', 'carbohydrates'
    ]
    
    df_cleaned = df[columns_to_keep].copy()
    
    # Save to CSV
    df_cleaned.to_csv(CLEANED_DATASET_PATH, index=False)
    print(f"✅ Saved cleaned dataset to: {CLEANED_DATASET_PATH}")
    print(f"   File size: {df_cleaned.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Save sample recipes for verification
    sample_file = 'cleaned_recipes_sample.txt'
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write("CLEANED RECIPES SAMPLE\n")
        f.write("="*80 + "\n\n")
        
        for i in range(5):
            recipe = df_cleaned.iloc[i]
            f.write(f"Recipe #{i+1}\n")
            f.write(f"Name: {recipe['name']}\n")
            f.write(f"Cooking Time: {recipe['minutes']} minutes\n")
            f.write(f"Difficulty: {recipe['difficulty']}\n")
            f.write(f"Ingredients ({recipe['n_ingredients']}): {recipe['ingredients'][:5]}\n")
            f.write(f"Dietary Tags: {recipe['dietary_tags']}\n")
            f.write(f"Cuisine Tags: {recipe['cuisine_tags']}\n")
            f.write(f"Calories: {recipe['calories']}\n")
            f.write("\n" + "="*80 + "\n\n")
    
    print(f"✅ Saved sample recipes to: {sample_file}")
    
    print("\n" + "="*80)
    print("🎉 CLEANING COMPLETE!")
    print("="*80)
    print("\nYour cleaned dataset is ready for the recommendation engine!")
    print("\nNext steps:")
    print("1. Review cleaned_recipes_sample.txt")
    print("2. Share results with Claude")
    print("3. Build the recommendation engine!")
    
    return df_cleaned

if __name__ == "__main__":
    cleaned_df = clean_recipes_dataset()