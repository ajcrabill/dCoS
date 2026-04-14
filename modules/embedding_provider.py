"""Embedding Provider: Local LLM-based embeddings via Ollama or MLX.

Supports multiple embedding backends without external API dependencies.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Embed a single text string."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is ready."""
        pass


class OllamaEmbedder(EmbeddingProvider):
    """Ollama-based embeddings (local, privacy-preserving)."""

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.embedding_dim = 768  # nomic-embed-text

    def embed(self, text: str) -> List[float]:
        """Single embedding via Ollama."""
        import requests
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            return response.json()["embedding"]
        except Exception as e:
            raise RuntimeError(f"Ollama embedding failed: {e}")

    def is_available(self) -> bool:
        """Check Ollama health."""
        try:
            import requests
            requests.get(f"{self.base_url}/api/tags", timeout=2)
            return True
        except:
            return False


class MLXEmbedder(EmbeddingProvider):
    """MLX-based embeddings (Apple Silicon native, fast)."""

    def __init__(self, model: str = "bert-base-uncased"):
        try:
            from transformers import AutoTokenizer, AutoModel
            self.model_name = model
            self.tokenizer = AutoTokenizer.from_pretrained(model)
            self.model = AutoModel.from_pretrained(model)
            self.embedding_dim = self.model.config.hidden_size
        except ImportError:
            raise RuntimeError("MLX not installed. Install: pip install mlx transformers")

    def embed(self, text: str) -> List[float]:
        """Single embedding via MLX."""
        inputs = self.tokenizer(text, return_tensors="mlx")
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(axis=1)
        return embeddings[0].tolist()

    def is_available(self) -> bool:
        """MLX available if import succeeded."""
        return True


def get_embedding_provider(backend: str = "ollama") -> EmbeddingProvider:
    """Factory function to get embedding provider.

    Args:
        backend: "ollama" (default) or "mlx"

    Returns:
        EmbeddingProvider instance
    """
    if backend == "ollama":
        return OllamaEmbedder()
    elif backend == "mlx":
        return MLXEmbedder()
    else:
        raise ValueError(f"Unknown backend: {backend}")


def list_available_backends() -> List[str]:
    """List available embedding backends."""
    available = []
    if OllamaEmbedder().is_available():
        available.append("ollama")
    try:
        if MLXEmbedder().is_available():
            available.append("mlx")
    except:
        pass
    return available
