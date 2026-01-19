import pandas as pd
import os

def convert_dataset():
    print("Converting dataset.xlsx to raw_recipes.csv...")
    
    try:
        df = pd.read_excel('dataset.xlsx')
        
        # Map columns
        new_df = pd.DataFrame()
        
        # Title
        new_df['title'] = df['TranslatedRecipeName']
        
        # Ingredients
        new_df['ingredients'] = df['TranslatedIngredients']
        
        # Cuisine
        new_df['cuisine'] = df['Cuisine']
        
        # Cook Time (add ' minutes' to make it parseable by our processor)
        new_df['cook_time'] = df['TotalTimeInMins'].astype(str) + " minutes"
        
        # Instructions
        new_df['instructions'] = df['TranslatedInstructions']
        
        # Image URL (using URL column)
        new_df['image_url'] = df['URL']
        
        # Servings
        new_df['servings'] = df['Servings']
        
        # Tags (Combine Diet and Course)
        new_df['tags'] = df['Diet'].fillna('') + " " + df['Course'].fillna('')
        
        # Description (Use RecipeName as description or just empty)
        new_df['description'] = df['RecipeName']
        
        # Drop rows where essential fields are missing
        new_df.dropna(subset=['title', 'ingredients'], inplace=True)
        
        # Fill other NaNs
        new_df.fillna('', inplace=True)
        
        # Save
        output_file = 'raw_recipes.csv'
        new_df.to_csv(output_file, index=False)
        print(f"Successfully created {output_file} with {len(new_df)} recipes.")
        print("Columns:", new_df.columns.tolist())
        
    except Exception as e:
        print(f"Error converting dataset: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_dataset()
