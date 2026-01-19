"""
Test suite for RecipeDataProcessor.
"""
import unittest
import pandas as pd
import tempfile
import os
from data_processor import RecipeDataProcessor


class TestRecipeDataProcessor(unittest.TestCase):
    """Test cases for RecipeDataProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = RecipeDataProcessor()
        
        # Sample recipe data for testing
        self.sample_recipes = [
            {
                'title': 'Spaghetti Carbonara',
                'ingredients': 'spaghetti, eggs, bacon, parmesan cheese, black pepper',
                'cuisine': 'Italian',
                'cook_time': '20 minutes',
                'difficulty': 'medium',
                'description': 'Classic Italian pasta dish',
                'instructions': 'Cook pasta, mix with eggs and cheese',
                'servings': 4
            },
            {
                'title': 'Vegan Buddha Bowl',
                'ingredients': 'quinoa, chickpeas, avocado, spinach, tahini',
                'tags': 'vegan, healthy, gluten-free',
                'total_time': '45 min',
                'description': 'Nutritious vegan bowl',
                'servings': 2
            },
            {
                'title': 'Chicken Tikka Masala',
                'ingredients': 'chicken, tomatoes, cream, spices, onions, garlic',
                'cuisine': 'Indian',
                'cook_time': '1 hour 30 minutes',
                'difficulty': 'hard',
                'description': 'Creamy Indian curry',
                'servings': 6
            },
            {
                'title': 'Quick Stir Fry',
                'ingredients': 'vegetables, soy sauce, garlic, ginger',
                'cook_time': '15 min',
                'tags': 'quick, vegetarian, asian',
                'servings': 3
            }
        ]
    
    def test_extract_cuisine(self):
        """Test cuisine extraction."""
        # Test explicit cuisine field
        recipe1 = {'cuisine': 'Italian'}
        self.assertEqual(self.processor.extract_cuisine(recipe1), 'Italian')
        
        # Test cuisine in title
        recipe2 = {'title': 'Thai Green Curry'}
        self.assertEqual(self.processor.extract_cuisine(recipe2), 'Thai')
        
        # Test cuisine in tags
        recipe3 = {'tags': 'mexican, spicy, authentic'}
        self.assertEqual(self.processor.extract_cuisine(recipe3), 'Mexican')
        
        # Test unknown cuisine
        recipe4 = {'title': 'Random Recipe'}
        self.assertEqual(self.processor.extract_cuisine(recipe4), 'Other')
    
    def test_extract_diet_type(self):
        """Test diet type extraction."""
        # Test explicit diet tags
        recipe1 = {'tags': 'vegan, gluten-free'}
        diet_types = self.processor.extract_diet_type(recipe1)
        self.assertIn('Vegan', diet_types)
        self.assertIn('Gluten-Free', diet_types)
        
        # Test diet in title
        recipe2 = {'title': 'Keto Friendly Salad'}
        diet_types = self.processor.extract_diet_type(recipe2)
        self.assertIn('Keto', diet_types)
        
        # Test no specific diet
        recipe3 = {'title': 'Regular Pasta'}
        diet_types = self.processor.extract_diet_type(recipe3)
        self.assertEqual(diet_types, ['Regular'])
    
    def test_extract_cooking_time(self):
        """Test cooking time extraction."""
        # Test minutes format
        recipe1 = {'cook_time': '30 minutes'}
        self.assertEqual(self.processor.extract_cooking_time(recipe1), 30)
        
        # Test hours and minutes
        recipe2 = {'total_time': '1 hour 15 minutes'}
        self.assertEqual(self.processor.extract_cooking_time(recipe2), 75)
        
        # Test abbreviated format
        recipe3 = {'cook_time': '45 min'}
        self.assertEqual(self.processor.extract_cooking_time(recipe3), 45)
        
        # Test hours only
        recipe4 = {'cook_time': '2 hours'}
        self.assertEqual(self.processor.extract_cooking_time(recipe4), 120)
        
        # Test no time (should default to 30)
        recipe5 = {'title': 'No Time Recipe'}
        self.assertEqual(self.processor.extract_cooking_time(recipe5), 30)
    
    def test_extract_difficulty(self):
        """Test difficulty extraction."""
        # Test explicit difficulty
        recipe1 = {'difficulty': 'easy'}
        self.assertEqual(self.processor.extract_difficulty(recipe1), 'Easy')
        
        recipe2 = {'difficulty': 'hard'}
        self.assertEqual(self.processor.extract_difficulty(recipe2), 'Hard')
        
        # Test heuristic based on time and ingredients
        recipe3 = {
            'cook_time': '15 minutes',
            'ingredients': 'pasta, sauce, cheese'
        }
        self.assertEqual(self.processor.extract_difficulty(recipe3), 'Easy')
        
        recipe4 = {
            'cook_time': '2 hours',
            'ingredients': 'flour, yeast, water, salt, olive oil, tomatoes, mozzarella, basil, oregano, garlic, onions, pepperoni, mushrooms, peppers, olives'
        }
        self.assertEqual(self.processor.extract_difficulty(recipe4), 'Hard')
    
    def test_validate_recipe_data(self):
        """Test recipe data validation."""
        # Valid recipe
        valid_recipe = {
            'title': 'Test Recipe',
            'ingredients': 'ingredient1, ingredient2'
        }
        self.assertTrue(self.processor.validate_recipe_data(valid_recipe))
        
        # Missing title
        invalid_recipe1 = {
            'ingredients': 'ingredient1, ingredient2'
        }
        self.assertFalse(self.processor.validate_recipe_data(invalid_recipe1))
        
        # Missing ingredients
        invalid_recipe2 = {
            'title': 'Test Recipe'
        }
        self.assertFalse(self.processor.validate_recipe_data(invalid_recipe2))
        
        # Empty ingredients
        invalid_recipe3 = {
            'title': 'Test Recipe',
            'ingredients': ''
        }
        self.assertFalse(self.processor.validate_recipe_data(invalid_recipe3))
    
    def test_process_recipe_dataset(self):
        """Test full dataset processing."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame(self.sample_recipes)
            df.to_csv(f.name, index=False)
            input_file = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Process the dataset
            processed_df = self.processor.process_recipe_dataset(input_file, output_file)
            
            # Verify output
            self.assertEqual(len(processed_df), 4)  # All recipes should be valid
            
            # Check required columns exist
            required_columns = [
                'id', 'title', 'ingredients_raw', 'ingredients_cleaned',
                'cuisine', 'diet_types', 'cooking_time', 'difficulty',
                'ingredient_count'
            ]
            for col in required_columns:
                self.assertIn(col, processed_df.columns)
            
            # Check specific values
            carbonara_row = processed_df[processed_df['title'] == 'Spaghetti Carbonara'].iloc[0]
            self.assertEqual(carbonara_row['cuisine'], 'Italian')
            self.assertEqual(carbonara_row['cooking_time'], 20)
            self.assertEqual(carbonara_row['difficulty'], 'Medium')
            
            buddha_bowl_row = processed_df[processed_df['title'] == 'Vegan Buddha Bowl'].iloc[0]
            self.assertIn('Vegan', buddha_bowl_row['diet_types'])
            self.assertIn('Gluten-Free', buddha_bowl_row['diet_types'])
            
            # Verify output file was created
            self.assertTrue(os.path.exists(output_file))
            
            # Load and verify saved data
            saved_df = pd.read_csv(output_file)
            self.assertEqual(len(saved_df), len(processed_df))
            
        finally:
            # Clean up temporary files
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == '__main__':
    unittest.main()