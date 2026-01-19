"""
Validation script to verify that the recipe data structuring system meets all requirements.
"""
import pandas as pd
import os

def validate_recipes_cleaned_csv():
    """
    Validate that recipes_cleaned.csv meets all requirements from task 1.2.
    
    Requirements 5.3, 5.4:
    - Extract and normalize cuisine, diet, cooking_time, and difficulty columns
    - Implement data validation for structured fields
    - Create recipes_cleaned.csv output with all processed data
    """
    
    output_file = "recipes_cleaned.csv"
    
    print("Validating recipes_cleaned.csv output...")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(output_file):
        print("❌ FAIL: recipes_cleaned.csv file not found")
        return False
    
    print("✅ PASS: recipes_cleaned.csv file exists")
    
    # Load the data
    try:
        df = pd.read_csv(output_file)
        print(f"✅ PASS: Successfully loaded CSV with {len(df)} records")
    except Exception as e:
        print(f"❌ FAIL: Could not load CSV file: {e}")
        return False
    
    # Check required columns exist
    required_columns = [
        'id', 'title', 'ingredients_raw', 'ingredients_cleaned',
        'cuisine', 'diet_types', 'cooking_time', 'difficulty',
        'description', 'instructions', 'image_url', 'servings', 'ingredient_count'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ FAIL: Missing required columns: {missing_columns}")
        return False
    
    print("✅ PASS: All required columns present")
    
    # Validate cuisine normalization
    valid_cuisines = [
        'Italian', 'Chinese', 'Mexican', 'Indian', 'French', 'Thai', 'Japanese',
        'Mediterranean', 'American', 'Greek', 'Spanish', 'Korean', 'Middle Eastern',
        'Vietnamese', 'German', 'British', 'Other'
    ]
    
    invalid_cuisines = df[~df['cuisine'].isin(valid_cuisines)]['cuisine'].unique()
    if len(invalid_cuisines) > 0:
        print(f"❌ FAIL: Invalid cuisine values found: {invalid_cuisines}")
        return False
    
    print("✅ PASS: All cuisine values are properly normalized")
    
    # Validate diet types
    valid_diets = [
        'Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Paleo',
        'Low-Carb', 'Pescatarian', 'Nut-Free', 'Soy-Free', 'Regular'
    ]
    
    for diet_str in df['diet_types']:
        diets = [d.strip() for d in diet_str.split(',')]
        invalid_diets = [d for d in diets if d not in valid_diets]
        if invalid_diets:
            print(f"❌ FAIL: Invalid diet types found: {invalid_diets}")
            return False
    
    print("✅ PASS: All diet types are properly normalized")
    
    # Validate cooking time (should be positive integers)
    if not df['cooking_time'].dtype in ['int64', 'int32']:
        print("❌ FAIL: Cooking time should be integer values")
        return False
    
    if (df['cooking_time'] <= 0).any():
        print("❌ FAIL: Cooking time should be positive values")
        return False
    
    print("✅ PASS: Cooking times are valid positive integers")
    
    # Validate difficulty levels
    valid_difficulties = ['Easy', 'Medium', 'Hard']
    invalid_difficulties = df[~df['difficulty'].isin(valid_difficulties)]['difficulty'].unique()
    if len(invalid_difficulties) > 0:
        print(f"❌ FAIL: Invalid difficulty values found: {invalid_difficulties}")
        return False
    
    print("✅ PASS: All difficulty levels are properly normalized")
    
    # Validate ingredient processing
    if df['ingredients_cleaned'].isnull().any():
        print("❌ FAIL: Some recipes have null cleaned ingredients")
        return False
    
    if (df['ingredient_count'] <= 0).any():
        print("❌ FAIL: All recipes should have at least one ingredient")
        return False
    
    print("✅ PASS: Ingredients are properly cleaned and counted")
    
    # Validate data completeness
    required_fields = ['title', 'ingredients_raw', 'ingredients_cleaned']
    for field in required_fields:
        if df[field].isnull().any() or (df[field] == '').any():
            print(f"❌ FAIL: Required field '{field}' has missing values")
            return False
    
    print("✅ PASS: All required fields have valid data")
    
    # Display summary statistics
    print("\n" + "=" * 50)
    print("DATASET SUMMARY")
    print("=" * 50)
    print(f"Total recipes: {len(df)}")
    print(f"Average cooking time: {df['cooking_time'].mean():.1f} minutes")
    print(f"Average ingredients per recipe: {df['ingredient_count'].mean():.1f}")
    
    print(f"\nCuisine distribution:")
    for cuisine, count in df['cuisine'].value_counts().items():
        print(f"  {cuisine}: {count}")
    
    print(f"\nDifficulty distribution:")
    for difficulty, count in df['difficulty'].value_counts().items():
        print(f"  {difficulty}: {count}")
    
    print("\n✅ ALL VALIDATIONS PASSED!")
    print("The recipe data structuring system successfully meets all requirements.")
    
    return True

def main():
    """Main validation function."""
    success = validate_recipes_cleaned_csv()
    
    if success:
        print("\n🎉 Task 1.2 'Build recipe data structuring system' is COMPLETE!")
        print("\nRequirements satisfied:")
        print("✅ Extract and normalize cuisine, diet, cooking_time, and difficulty columns")
        print("✅ Implement data validation for structured fields") 
        print("✅ Create recipes_cleaned.csv output with all processed data")
        print("✅ Requirements 5.3, 5.4 fulfilled")
    else:
        print("\n❌ Validation failed. Please check the implementation.")

if __name__ == "__main__":
    main()