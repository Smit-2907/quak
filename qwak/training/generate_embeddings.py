#!/usr/bin/env python3
"""
Generate Sentence-BERT embeddings for recipe ingredients and create FAISS index.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from typing import List, Tuple
import time

def main():
    # Load the cleaned recipe data
    print('Loading cleaned recipe data...')
    df = pd.read_csv('recipes_cleaned.csv')
    print(f'Loaded {len(df)} recipes')

    # Initialize Sentence-BERT model
    print('Loading Sentence-BERT model (MiniLM-L6-v2)...')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f'Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}')

    # Prepare ingredient texts for embedding
    print('Preparing ingredient texts...')
    ingredient_texts = df['ingredients_cleaned'].fillna('').tolist()
    print(f'Sample ingredient text: {ingredient_texts[0]}')

    # Generate embeddings
    print('Generating embeddings...')
    start_time = time.time()
    ingredient_sentences = [text.replace(',', ' ') for text in ingredient_texts]
    embeddings = model.encode(ingredient_sentences, 
                             batch_size=32, 
                             show_progress_bar=True, 
                             convert_to_numpy=True)
    end_time = time.time()
    print(f'Embedding generation completed in {end_time - start_time:.2f} seconds')
    print(f'Embeddings shape: {embeddings.shape}')

    # Save embeddings
    print('Saving embeddings...')
    np.save('recipe_vectors_embed.npy', embeddings)
    print('Embeddings saved to recipe_vectors_embed.npy')

    # Create FAISS index
    print('Creating FAISS index...')
    dimension = embeddings.shape[1]
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    print(f'FAISS index created with {index.ntotal} vectors')

    # Save FAISS index
    print('Saving FAISS index...')
    faiss.write_index(index, 'recipe_faiss_index.bin')
    print('FAISS index saved to recipe_faiss_index.bin')

    # Test the index
    print('Testing FAISS index...')
    test_ingredients = 'chicken, garlic, onion'
    test_embedding = model.encode([test_ingredients.replace(',', ' ')], convert_to_numpy=True)
    faiss.normalize_L2(test_embedding)
    k = 5
    scores, indices = index.search(test_embedding, k)

    print(f'\nTest query: {test_ingredients}')
    print('Top 5 similar recipes:')
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        recipe = df.iloc[idx]
        print(f'{i+1}. {recipe["title"]} (Score: {score:.4f})')
        print(f'   Ingredients: {recipe["ingredients_cleaned"]}')

    # Save metadata
    metadata = {
        'model_name': 'all-MiniLM-L6-v2',
        'embedding_dimension': dimension,
        'num_recipes': len(df),
        'index_type': 'IndexFlatIP',
        'normalized': True
    }

    with open('embedding_metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)

    print('\nMetadata saved to embedding_metadata.pkl')
    print('=== Embedding Generation Complete ===')
    print(f'Generated embeddings for {len(df)} recipes')
    print(f'Embedding dimension: {dimension}')
    print(f'Files created:')
    print(f'  - recipe_vectors_embed.npy ({embeddings.nbytes / 1024 / 1024:.2f} MB)')
    print(f'  - recipe_faiss_index.bin')
    print(f'  - embedding_metadata.pkl')

if __name__ == '__main__':
    main()