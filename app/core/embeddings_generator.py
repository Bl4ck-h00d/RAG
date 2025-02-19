from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2')

    def generate(self, text: str) -> list[float]:
        embedding = self.model.encode(text, convert_to_tensor=False)

        return embedding.tolist()
