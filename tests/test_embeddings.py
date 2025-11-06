import numpy as np

from config import AppConfig, ensure_output_dirs
from services.semantic_service import SemanticAnalyzer


class DummyEmbeddingModel:
    def encode(self, text, convert_to_numpy=True):
        return np.ones(4, dtype=float)


def test_build_semantic_clusters_with_dummy_model(monkeypatch, tmp_path):
    config = AppConfig(outputs_dir=tmp_path / "outputs", chunk_size=50, chunk_overlap=10)
    ensure_output_dirs(config)
    analyzer = SemanticAnalyzer(config)
    monkeypatch.setattr(analyzer.model_loader, "load_model", lambda: DummyEmbeddingModel())

    segments = [
        {"id": 1, "start": 0.0, "end": 3.0, "text": "Item um da reunião."},
        {"id": 2, "start": 3.0, "end": 6.0, "text": "Discussão de decisões importantes."},
    ]

    clusters = analyzer.build_semantic_clusters(segments)

    assert clusters, "Deve gerar ao menos um cluster com modelo dummy."
    assert clusters[0].text, "Texto agregado não pode estar vazio."


def test_normalize_vector_handles_zero_norm():
    vec = np.zeros(4, dtype=float)
    normalized = SemanticAnalyzer._normalize_vector(vec)
    assert np.allclose(normalized, np.zeros(4))
