#!/usr/bin/env python3
"""
Full training pipeline for QWAK Recipe Recommender.
1. Processes raw dataset (raw_recipes.csv) -> recipes_cleaned.csv
2. Trains TF-IDF model -> backend/models/
3. Generates Embeddings -> backend/models/
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
import sys
from pathlib import Path
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_processor import RecipeDataProcessor

def setup_directories():
    """Ensure model directory exists."""
    # Assuming we are in qwak/training/
    base_dir = Path(__file__).parent.parent
    models_dir = base_dir / "backend" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir

def process_data(input_file="raw_recipes.csv"):
    """Step 1: Process raw data."""
    print("\n=== Step 1: Processing Data ===")
    processor = RecipeDataProcessor()
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please place your dataset in the training directory.")
        return None
        
    output_file = "recipes_cleaned.csv"
    df = processor.process_recipe_dataset(input_file, output_file)
    return df

def train_tfidf(df, models_dir):
    """Step 2: Train TF-IDF Model."""
    print("\n=== Step 2: Training TF-IDF Model ===")
    
    # Prepare text
    ingredient_texts = df['ingredients_cleaned'].fillna('').tolist()
    
    # Initialize vectorizer
    vectorizer = TfidfVectorizer(
        lowercase=True,
        token_pattern=r'[a-zA-Z]+',
        stop_words=None,
        max_features=5000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2)
    )
    
    print("Training vectorizer...")
    tfidf_matrix = vectorizer.fit_transform(ingredient_texts)
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    # Save vectorizer
    vectorizer_path = models_dir / 'vectorizer.pkl'
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"Saved vectorizer to {vectorizer_path}")
    
    # Save vectors
    vectors_path = models_dir / 'recipe_vectors_tfidf.npz'
    np.savez_compressed(vectors_path, vectors=tfidf_matrix.toarray())
    print(f"Saved vectors to {vectors_path}")
    
    # Save metadata
    metadata_path = models_dir / 'recipe_metadata.pkl'
    recipe_metadata = df[['id', 'title', 'ingredients_cleaned', 'cuisine', 'diet_types', 'cooking_time', 'difficulty']].to_dict('records')
    with open(metadata_path, 'wb') as f:
        pickle.dump(recipe_metadata, f)
    print(f"Saved metadata to {metadata_path}")

def train_embeddings(df, models_dir):
    """Step 3: Generate Embeddings."""
    print("\n=== Step 3: Generating Embeddings ===")
    
    print('Loading Sentence-BERT model (all-MiniLM-L6-v2)...')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    ingredient_texts = df['ingredients_cleaned'].fillna('').tolist()
    ingredient_sentences = [text.replace(',', ' ') for text in ingredient_texts]
    
    print('Generating embeddings...')
    embeddings = model.encode(ingredient_sentences, 
                             batch_size=32, 
                             show_progress_bar=True, 
                             convert_to_numpy=True)
    
    # Save embeddings
    embed_path = models_dir / 'recipe_vectors_embed.npy'
    np.save(embed_path, embeddings)
    print(f"Saved embeddings to {embed_path}")
    
    # Create and save FAISS index
    print('Creating FAISS index...')
    dimension = embeddings.shape[1]
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    index_path = models_dir / 'recipe_faiss_index.bin'
    faiss.write_index(index, str(index_path))
    print(f"Saved FAISS index to {index_path}")
    
    # Save embedding metadata
    meta_path = models_dir / 'embedding_metadata.pkl'
    metadata = {
        'model_name': 'all-MiniLM-L6-v2',
        'embedding_dimension': dimension,
        'num_recipes': len(df),
        'index_type': 'IndexFlatIP',
        'normalized': True
    }
    with open(meta_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved embedding metadata to {meta_path}")

def main():
    print("Starting QWAK Full Training Pipeline...")
    
    # Setup
    models_dir = setup_directories()
    
    # Check for input file
    input_file = "raw_recipes.csv"
    if not os.path.exists(input_file):
        # Fallback to sample if raw not found, but warn user
        if os.path.exists("sample_recipes.csv"):
            print(f"Warning: '{input_file}' not found. Using 'sample_recipes.csv' instead.")
            input_file = "sample_recipes.csv"
        else:
            print(f"Error: No input file found. Please place 'raw_recipes.csv' in {os.getcwd()}")
            return
    
    # Execute pipeline
    df = process_data(input_file)
    if df is not None:
        train_tfidf(df, models_dir)
        train_embeddings(df, models_dir)
        print("\n=== Training Complete! ===")
        print("You can now restart the backend to use the new models.")

if __name__ == "__main__":
    main()
