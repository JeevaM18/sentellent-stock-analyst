import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.embeddings import GoogleEmbeddingProvider, EmbeddingProviderError


def test_embedding_cli():
    print("=" * 60)
    print("Testing Google Generative AI text-embedding-004 Provider")
    print("=" * 60)

    provider = GoogleEmbeddingProvider()
    sample_text = "Reliance Industries announced strong quarterly earnings performance."

    try:
        res = provider.embed_text(text=sample_text, metadata={"sector": "Energy"})

        vec = res.vector
        min_val = min(vec)
        max_val = max(vec)
        mean_val = sum(vec) / len(vec)

        print(f"\nModel      : {res.model}")
        print(f"Provider   : {res.provider}")
        print(f"Dimensions : {res.dimensions}")
        print(f"Vector Len : {len(vec)}")
        print(f"Min Value  : {min_val:.6f}")
        print(f"Max Value  : {max_val:.6f}")
        print(f"Mean Value : {mean_val:.6f}")
        print(f"\nFirst 10 Values:\n{vec[:10]}")
        print(f"\nMetadata   : {res.metadata}")
        print(f"Created At : {res.created_at.isoformat()}")
        print("=" * 60)
        print("SUCCESS: GoogleEmbeddingProvider is functional!")

    except EmbeddingProviderError as e:
        print(f"Embedding Provider Error: {e}")
    except Exception as e:
        print(f"Execution Error: {e}")


if __name__ == "__main__":
    test_embedding_cli()
