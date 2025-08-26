import sys
import os
import unittest
import pandas as pd

# Fix import to allow finding movie_search module in parent folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from movie_search import search_movies, load_movies


class TestMovieSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load movies.csv and embeddings once for all tests
        load_movies(os.path.join(parent_dir, 'movies.csv'))

    def setUp(self):
        # Print a separator before each test for clarity in local runs
        print("\n" + "="*70)

    def test_search_movies_output_format(self):
        """Test search_movies returns a DataFrame with expected columns."""
        query = "spy thriller in Paris"
        result = search_movies(query, top_n=3)
        self.assertIsInstance(result, pd.DataFrame, "Result should be a pandas DataFrame")
        expected_columns = {'title', 'plot', 'similarity'}
        self.assertTrue(expected_columns.issubset(result.columns),
                        f"Result should have columns: {expected_columns}")

    def test_search_movies_top_n(self):
        """Test search_movies respects the top_n limit."""
        top_n = 2
        query = "spy thriller in Paris"
        result = search_movies(query, top_n=top_n)
        self.assertEqual(len(result), top_n, f"Result should return {top_n} movies")

    def test_search_movies_similarity_range(self):
        """Test similarity scores are between 0 and 1 within tolerance."""
        query = "spy thriller in Paris"
        result = search_movies(query, top_n=3)
        similarities = result['similarity'].values
        for sim in similarities:
            self.assertGreaterEqual(sim, 0.0, f"Similarity {sim} below 0")
            self.assertLessEqual(sim, 1.0, f"Similarity {sim} above 1")

    def test_search_movies_relevance(self):
        """Test if top result plot contains key query terms."""
        query = "spy thriller in Paris"
        result = search_movies(query, top_n=1)
        top_plot = result.iloc[0]['plot'].lower()
        self.assertTrue(any(term in top_plot for term in ['spy', 'thriller', 'paris']),
                        "Top result plot should contain query terms")

    def test_search_movies_expected_titles_spy(self):
        """Check returned titles include 'Spy Movie' for spy thriller query."""
        query = "spy thriller in Paris"
        result = search_movies(query, top_n=3)
        titles = result['title'].values
        self.assertIn('Spy Movie', titles,
                      "Expected 'Spy Movie' in results for spy thriller query")

    def test_search_movies_expected_titles_romance(self):
        """Check returned titles include 'Romance in Paris' for romantic query."""
        query = "romantic movie in Paris"
        result = search_movies(query, top_n=3)
        titles = result['title'].values
        self.assertIn('Romance in Paris', titles,
                      "Expected 'Romance in Paris' in results for romantic query")

    def test_search_movies_expected_titles_action(self):
        """Check returned titles include 'Action Flick' for action movie query."""
        query = "explosions chase New York"
        result = search_movies(query, top_n=3)
        titles = result['title'].values
        self.assertIn('Action Flick', titles,
                      "Expected 'Action Flick' in results for action query")


if __name__ == '__main__':
    unittest.main(verbosity=2)
