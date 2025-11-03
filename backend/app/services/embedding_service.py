"""
Embedding generation service using sentence-transformers for semantic search
"""
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.models import db, Item
import numpy as np


class EmbeddingService:
    """Singleton service for generating and searching embeddings"""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            # Load the model once (384-dimension embeddings)
            # This model is optimized for semantic similarity
            self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding vector from text

        Args:
            text: Input text (item description)

        Returns:
            List of 384 floats representing the embedding
        """
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: list) -> list:
        """
        Generate embeddings for multiple texts efficiently

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def find_similar_items(self, query_text: str = None, query_embedding: list = None,
                          threshold: float = 0.85, limit: int = 10, exclude_id: int = None):
        """
        Find items similar to a query using vector similarity search

        Args:
            query_text: Text to search for (will generate embedding)
            query_embedding: Pre-computed embedding vector
            threshold: Minimum cosine similarity (0.0-1.0)
            limit: Maximum number of results
            exclude_id: Item ID to exclude from results

        Returns:
            List of tuples: (item, similarity_score)
        """
        # Generate embedding if text provided
        if query_text:
            query_embedding = self.generate_embedding(query_text)

        if query_embedding is None:
            raise ValueError("Must provide either query_text or query_embedding")

        # Convert to pgvector format string
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        print(f"DEBUG: Searching with threshold={threshold}, limit={limit}, exclude_id={exclude_id}")
        print(f"DEBUG: Embedding length: {len(query_embedding)}")
        print(f"DEBUG: Embedding first 5 values: {query_embedding[:5]}")

        # SQL query using pgvector's cosine similarity operator (<=>)
        # Lower distance = higher similarity, so we use 1 - distance
        # Note: embedding_str is safely formatted (not user input), so we use string formatting
        sql = text(f"""
            SELECT id, name, description, category,
                   1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM items
            WHERE embedding IS NOT NULL
                AND (:exclude_id IS NULL OR id != :exclude_id)
                AND 1 - (embedding <=> '{embedding_str}'::vector) >= :threshold
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT :limit
        """)

        print(f"DEBUG: Executing SQL query...")
        results = db.session.execute(
            sql,
            {
                'threshold': threshold,
                'limit': limit,
                'exclude_id': exclude_id
            }
        )

        # Convert results to Item objects with similarity scores
        similar_items = []
        for row in results:
            print(f"DEBUG: Found item {row.id} with similarity {row.similarity}")
            item = Item.query.get(row.id)
            if item:
                similar_items.append((item, float(row.similarity)))

        print(f"DEBUG: Returning {len(similar_items)} similar items")
        return similar_items

    def find_duplicates_for_item(self, item: Item, threshold: float = 0.85):
        """
        Find potential duplicates for a specific item

        Args:
            item: Item instance with embedding
            threshold: Minimum similarity score to consider as duplicate

        Returns:
            List of tuples: (similar_item, similarity_score)
        """
        if item.embedding is None:
            return []

        return self.find_similar_items(
            query_embedding=item.embedding,
            threshold=threshold,
            exclude_id=item.id
        )


# Singleton instance
embedding_service = EmbeddingService()
