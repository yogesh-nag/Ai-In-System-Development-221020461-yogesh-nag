"""
movie_search.py

A semantic search engine for movie plots using the SentenceTransformers model all-MiniLM-L6-v2.

Features:
- Loads movie data from CSV.
- Encodes movie plots into embeddings.
- Searches movies based on query semantic similarity.
- Handles edge cases: missing files, empty inputs, missing columns.
- Well documented with function level and inline comments.
"""

import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class MovieSearcher:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize the MovieSearcher instance.

        Args:
            model_name (str): HuggingFace model name to use for encoding.
        """
        self.model_name = model_name
        self.model = None
        self.df_movies = None
        self.plot_embeddings = None

    def load_model(self):
        """
        Loads the SentenceTransformer model.

        Raises:
            RuntimeError: If model loading fails.
        """
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Error loading model '{self.model_name}': {e}")

    def load_movies(self, filepath='movies.csv'):
        """
        Loads movies CSV and computes plot embeddings.

        Args:
            filepath (str): Path to CSV file containing movie data.

        Raises:
            FileNotFoundError: If CSV file doesn't exist.
            ValueError: If required columns are missing.
            RuntimeError: If embeddings computation fails.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Movies CSV file not found at path: {filepath}")

        self.df_movies = pd.read_csv(filepath)

        # Validate required columns
        required_cols = {'title', 'plot'}
        if not required_cols.issubset(self.df_movies.columns):
            missing = required_cols - set(self.df_movies.columns)
            raise ValueError(f"Missing required columns in CSV: {missing}")

        # Drop rows with empty or NaN plots or titles
        self.df_movies.dropna(subset=['plot', 'title'], inplace=True)
        self.df_movies = self.df_movies[self.df_movies['plot'].str.strip() != '']
        if self.df_movies.empty:
            raise ValueError("No valid movie plots available after cleaning.")

        # Ensure model is loaded before embeddings
        if self.model is None:
            self.load_model()

        try:
            # Compute plot embeddings with progress bar
            self.plot_embeddings = self.model.encode(self.df_movies['plot'].tolist(), show_progress_bar=True)
        except Exception as e:
            raise RuntimeError(f"Error computing embeddings: {e}")

    def search_movies(self, query, top_n=5):
        """
        Searches for movies most semantically similar to the input query.

        Args:
            query (str): The search query string.
            top_n (int): Number of top results to return.

        Returns:
            pandas.DataFrame: DataFrame of top_n movies sorted by similarity.
                              Columns include 'title', 'plot', 'similarity'.

        Raises:
            ValueError: For invalid query or if data is not loaded.
        """
        # Input validation
        if not isinstance(query, str) or query.strip() == '':
            raise ValueError("Query must be a non-empty string.")

        if not isinstance(top_n, int) or top_n <= 0:
            raise ValueError("top_n must be a positive integer.")

        if self.df_movies is None or self.plot_embeddings is None:
            raise ValueError("Movies data and embeddings are not loaded. Call load_movies() first.")

        # Encode query
        try:
            query_emb = self.model.encode([query])
        except Exception as e:
            raise RuntimeError(f"Failed to encode query: {e}")

        # Compute cosine similarities between the query and all movie plots
        try:
            similarities = cosine_similarity(query_emb, self.plot_embeddings)[0]
        except Exception as e:
            raise RuntimeError(f"Error computing cosine similarity: {e}")

        # Get indices of top_n most similar movies
        top_indices = similarities.argsort()[::-1][:top_n]

        # Prepare result DataFrame with similarity scores
        results = self.df_movies.iloc[top_indices].copy()
        results['similarity'] = similarities[top_indices]

        # Sort results by descending similarity for clarity
        results.sort_values(by='similarity', ascending=False, inplace=True)

        # Reset index for clean output
        results.reset_index(drop=True, inplace=True)

        return results[['title', 'plot', 'similarity']]


# Create a singleton instance of MovieSearcher
_searcher = MovieSearcher()

def load_movies(filepath='movies.csv'):
    """Load movie data and embeddings."""
    _searcher.load_movies(filepath)

def search_movies(query, top_n=5):
    """Search movies with the given query and top_n results."""
    return _searcher.search_movies(query, top_n)


if __name__ == "__main__":
    try:
        load_movies('movies.csv')
    except Exception as e:
        print(f"Failed to load movies: {e}")
        exit(1)

    query = "spy thriller in Paris"
    print(f"Search results for query: '{query}'")
    try:
        results = search_movies(query, top_n=5)
        print(results.to_string(index=False))
    except Exception as e:
        print(f"Error during search: {e}")
