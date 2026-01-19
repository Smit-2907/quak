"""
Recipe data processing and structuring utilities.
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add backend utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from utils.text_cleaner import TextCleaner


class RecipeDataProcessor:
    """Handles recipe data cleaning, structuring, and validation."""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.cuisine_mapping = self._create_cuisine_mapping()
        self.diet_mapping = self._create_diet_mapping()
    
    def _create_cuisine_mapping(self) -> Dict[str, str]:
        """Create mapping for cuisine normalization."""
        return {
            'italian': 'Italian',
            'chinese': 'Chinese', 
            'mexican': 'Mexican',
            'indian': 'Indian',
            'french': 'French',
            'thai': 'Thai',
            'japanese': 'Japanese',
            'mediterranean': 'Mediterranean',
            'american': 'American',
            'greek': 'Greek',
            'spanish': 'Spanish',
            'korean': 'Korean',
            'middle eastern': 'Middle Eastern',
            'vietnamese': 'Vietnamese',
            'german': 'German',
            'british': 'British'
        }
    
    def _create_diet_mapping(self) -> Dict[str, str]:
        """Create mapping for diet type normalization."""
        return {
            'vegetarian': 'Vegetarian',
            'vegan': 'Vegan',
            'gluten-free': 'Gluten-Free',
            'dairy-free': 'Dairy-Free',
            'keto': 'Keto',
            'paleo': 'Paleo',
            'low-carb': 'Low-Carb',
            'pescatarian': 'Pescatarian',
            'nut-free': 'Nut-Free',
            'soy-free': 'Soy-Free'
        }
    
    def extract_cuisine(self, recipe_data: Dict) -> str:
        """
        Extract and normalize cuisine type from recipe data.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Normalized cuisine string or 'Other' if not found
        """
        # Check various fields for cuisine information
        fields_to_check = ['cuisine', 'category', 'tags', 'title', 'description']
        
        for field in fields_to_check:
            if field in recipe_data and recipe_data[field]:
                text = str(recipe_data[field]).lower()
                
                # Check against known cuisines
                for cuisine_key, cuisine_value in self.cuisine_mapping.items():
                    if cuisine_key in text:
                        return cuisine_value
        
        return 'Other'
    
    def extract_diet_type(self, recipe_data: Dict) -> List[str]:
        """
        Extract diet types from recipe data.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            List of applicable diet types
        """
        diet_types = []
        
        # Check various fields for diet information
        fields_to_check = ['diet', 'dietary_restrictions', 'tags', 'title', 'description', 'ingredients']
        
        for field in fields_to_check:
            if field in recipe_data and recipe_data[field]:
                text = str(recipe_data[field]).lower()
                
                # Check against known diet types
                for diet_key, diet_value in self.diet_mapping.items():
                    if diet_key in text and diet_value not in diet_types:
                        diet_types.append(diet_value)
        
        return diet_types if diet_types else ['Regular']
    
    def extract_cooking_time(self, recipe_data: Dict) -> int:
        """
        Extract cooking time in minutes from recipe data.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Cooking time in minutes, or 30 as default
        """
        # Check various time fields
        time_fields = ['cook_time', 'cooking_time', 'total_time', 'prep_time', 'time']
        
        for field in time_fields:
            if field in recipe_data and recipe_data[field]:
                time_str = str(recipe_data[field]).lower()
                
                # Extract numbers from time string
                minutes = self._parse_time_string(time_str)
                if minutes > 0:
                    return minutes
        
        # Default to 30 minutes if no time found
        return 30
    
    def _parse_time_string(self, time_str: str) -> int:
        """
        Parse time string to extract minutes.
        
        Args:
            time_str: String containing time information
            
        Returns:
            Time in minutes
        """
        time_str = time_str.lower().strip()
        
        # Look for hour patterns
        hour_match = re.search(r'(\d+)\s*(?:hour|hr|h)', time_str)
        minute_match = re.search(r'(\d+)\s*(?:minute|min|m)', time_str)
        
        total_minutes = 0
        
        if hour_match:
            total_minutes += int(hour_match.group(1)) * 60
        
        if minute_match:
            total_minutes += int(minute_match.group(1))
        
        # If no specific time format, look for just numbers
        if total_minutes == 0:
            number_match = re.search(r'(\d+)', time_str)
            if number_match:
                num = int(number_match.group(1))
                # Assume it's minutes if under 10, hours if over
                total_minutes = num if num > 10 else num * 60
        
        return total_minutes
    
    def extract_difficulty(self, recipe_data: Dict) -> str:
        """
        Extract difficulty level from recipe data.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Difficulty level: 'Easy', 'Medium', or 'Hard'
        """
        # Check for explicit difficulty field
        if 'difficulty' in recipe_data and recipe_data['difficulty']:
            diff_str = str(recipe_data['difficulty']).lower()
            
            if any(word in diff_str for word in ['easy', 'simple', 'basic', 'beginner']):
                return 'Easy'
            elif any(word in diff_str for word in ['hard', 'difficult', 'complex', 'advanced']):
                return 'Hard'
            elif any(word in diff_str for word in ['medium', 'intermediate', 'moderate']):
                return 'Medium'
        
        # Estimate difficulty based on other factors
        cooking_time = self.extract_cooking_time(recipe_data)
        ingredient_count = 0
        
        if 'ingredients' in recipe_data:
            ingredients = recipe_data['ingredients']
            if isinstance(ingredients, list):
                ingredient_count = len(ingredients)
            elif isinstance(ingredients, str):
                ingredient_count = len(ingredients.split(','))
        
        # Simple heuristic for difficulty
        if cooking_time <= 30 and ingredient_count <= 8:
            return 'Easy'
        elif cooking_time >= 90 or ingredient_count >= 15:
            return 'Hard'
        else:
            return 'Medium'
    
    def validate_recipe_data(self, recipe: Dict) -> bool:
        """
        Validate that recipe has required fields.
        
        Args:
            recipe: Recipe dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'ingredients']
        
        for field in required_fields:
            if field not in recipe or not recipe[field]:
                return False
        
        # Validate ingredients is not empty
        ingredients = recipe['ingredients']
        if isinstance(ingredients, list) and len(ingredients) == 0:
            return False
        elif isinstance(ingredients, str) and len(ingredients.strip()) == 0:
            return False
        
        return True
    
    def process_recipe_dataset(self, input_file: str, output_file: str) -> pd.DataFrame:
        """
        Process raw recipe dataset and create cleaned version.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output cleaned CSV file
            
        Returns:
            Processed DataFrame
        """
        print(f"Loading recipe data from {input_file}...")
        
        # Load the dataset
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} recipes")
        
        # Process each recipe
        processed_recipes = []
        
        for idx, row in df.iterrows():
            recipe_dict = row.to_dict()
            
            # Validate recipe
            if not self.validate_recipe_data(recipe_dict):
                continue
            
            # Extract structured information
            processed_recipe = {
                'id': idx,
                'title': recipe_dict.get('title', ''),
                'ingredients_raw': recipe_dict.get('ingredients', ''),
                'cuisine': self.extract_cuisine(recipe_dict),
                'diet_types': ','.join(self.extract_diet_type(recipe_dict)),
                'cooking_time': self.extract_cooking_time(recipe_dict),
                'difficulty': self.extract_difficulty(recipe_dict),
                'description': recipe_dict.get('description', ''),
                'instructions': recipe_dict.get('instructions', ''),
                'image_url': recipe_dict.get('image_url', ''),
                'servings': recipe_dict.get('servings', 4)
            }
            
            # Clean ingredients
            if isinstance(recipe_dict['ingredients'], str):
                ingredients_list = self.text_cleaner.clean_ingredient_list(recipe_dict['ingredients'])
            else:
                ingredients_list = self.text_cleaner.process_ingredients(recipe_dict['ingredients'])
            
            processed_recipe['ingredients_cleaned'] = ','.join(ingredients_list)
            processed_recipe['ingredient_count'] = len(ingredients_list)
            
            processed_recipes.append(processed_recipe)
        
        # Create DataFrame
        processed_df = pd.DataFrame(processed_recipes)
        
        print(f"Processed {len(processed_df)} valid recipes")
        print(f"Cuisine distribution:")
        print(processed_df['cuisine'].value_counts())
        print(f"\nDifficulty distribution:")
        print(processed_df['difficulty'].value_counts())
        
        # Save processed data
        processed_df.to_csv(output_file, index=False)
        print(f"Saved cleaned data to {output_file}")
        
        return processed_df


def main():
    """Main function to process recipe data."""
    processor = RecipeDataProcessor()
    
    # Example usage - you'll need to provide your actual input file
    input_file = "raw_recipes.csv"  # Replace with your input file
    output_file = "recipes_cleaned.csv"
    
    if os.path.exists(input_file):
        processed_df = processor.process_recipe_dataset(input_file, output_file)
        print(f"Processing complete! Cleaned dataset saved as {output_file}")
    else:
        print(f"Input file {input_file} not found. Please provide your recipe dataset.")
        print("Expected columns: title, ingredients, and optionally: cuisine, diet, cook_time, difficulty, description, instructions, image_url")


if __name__ == "__main__":
    main()