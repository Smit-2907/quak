"""
Script to process sample recipe data and create recipes_cleaned.csv
"""
from data_processor import RecipeDataProcessor
import os

def main():
    """Process the sample recipe dataset."""
    processor = RecipeDataProcessor()
    
    input_file = "sample_recipes.csv"
    output_file = "recipes_cleaned.csv"
    
    print("Processing sample recipe dataset...")
    processed_df = processor.process_recipe_dataset(input_file, output_file)
    
    print(f"\nDataset processing complete!")
    print(f"Input: {input_file} ({len(processed_df)} recipes)")
    print(f"Output: {output_file}")
    
    print(f"\nDataset Statistics:")
    print(f"Total recipes processed: {len(processed_df)}")
    print(f"Average cooking time: {processed_df['cooking_time'].mean():.1f} minutes")
    print(f"Average ingredients per recipe: {processed_df['ingredient_count'].mean():.1f}")
    
    print(f"\nCuisine Distribution:")
    cuisine_counts = processed_df['cuisine'].value_counts()
    for cuisine, count in cuisine_counts.items():
        print(f"  {cuisine}: {count}")
    
    print(f"\nDifficulty Distribution:")
    difficulty_counts = processed_df['difficulty'].value_counts()
    for difficulty, count in difficulty_counts.items():
        print(f"  {difficulty}: {count}")
    
    print(f"\nDiet Types Found:")
    all_diets = []
    for diet_str in processed_df['diet_types']:
        all_diets.extend(diet_str.split(','))
    diet_counts = {}
    for diet in all_diets:
        diet = diet.strip()
        diet_counts[diet] = diet_counts.get(diet, 0) + 1
    
    for diet, count in sorted(diet_counts.items()):
        print(f"  {diet}: {count}")
    
    print(f"\nSample processed recipes:")
    for idx, row in processed_df.head(3).iterrows():
        print(f"\n{idx + 1}. {row['title']}")
        print(f"   Cuisine: {row['cuisine']}")
        print(f"   Diet: {row['diet_types']}")
        print(f"   Time: {row['cooking_time']} min")
        print(f"   Difficulty: {row['difficulty']}")
        print(f"   Ingredients: {row['ingredients_cleaned'][:80]}...")

if __name__ == "__main__":
    main()