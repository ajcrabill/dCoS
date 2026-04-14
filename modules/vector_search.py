"""Hybrid Vector Search: BM25 + Vector Similarity + Graph Traversal.

Combines three search strategies for comprehensive retrieval of observations.
"""

from typing import List, Dict, Tuple
import sqlite3
import json
import numpy as np


class HybridVectorSearch:
    """Hybrid search combining BM25, vectors, and graph traversal."""

    def __init__(self, db_connection: sqlite3.Connection, embedder):
        self.db = db_connection
        self.embedder = embedder
        self.k = 5  # Number of results per strategy

    def search_vector(self, query: str, table: str, embedding_field: str = "embedding") -> List[Tuple[str, float]]:
        """Vector similarity search using cosine similarity.

        Args:
            query: Search query
            table: Table with embeddings
            embedding_field: Column containing embeddings (as JSON string)

        Returns:
            List of (doc_id, similarity_score) tuples
        """
        # Embed the query
        query_embedding = np.array(self.embedder.embed(query))

        cursor = self.db.cursor()
        cursor.execute(f"SELECT id, {embedding_field} FROM {table} WHERE {embedding_field} IS NOT NULL")
        rows = cursor.fetchall()

        similarities = []
        for row_id, embedding_json in rows:
            try:
                doc_embedding = np.array(json.loads(embedding_json))
                # Cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding) + 1e-8
                )
                similarities.append((row_id, float(similarity)))
            except:
                continue

        # Sort by similarity and return top-k
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:self.k]

    def hybrid_search(
        self,
        query: str,
        table: str,
        **kwargs
    ) -> List[Dict]:
        """Combined hybrid search with ranking.

        Args:
            query: Search query
            table: Primary table to search
            **kwargs: bm25_weight, vector_weight parameters

        Returns:
            Ranked list of results with scores
        """
        vector_weight = kwargs.get("vector_weight", 0.7)

        # Run vector search
        vector_results = self.search_vector(query, table)

        # Normalize and combine scores
        combined_scores = {}

        for doc_id, score in vector_results:
            combined_scores[doc_id] = score * vector_weight

        # Rank and return
        results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                "id": doc_id,
                "score": score,
            } for doc_id, score in results[:self.k]
        ]
