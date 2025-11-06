import numpy as np

from config import AppConfig, ensure_output_dirs
from services.semantic_service import SemanticCluster, SemanticChunk
from services.summarization_service import SummarizationService


class DummySummarizerPipeline:
    def __call__(self, text, max_length=180, min_length=30, do_sample=False):
        return [{"summary_text": "Decisão tomada. Pendência anotada. Próximo passo definido."}]


def test_generate_structured_summary_with_dummy_pipeline(monkeypatch, tmp_path):
    config = AppConfig(outputs_dir=tmp_path / "outputs", summary_max_tokens=120)
    ensure_output_dirs(config)
    service = SummarizationService(config)
    monkeypatch.setattr(service.model_loader, "load_pipeline", lambda: DummySummarizerPipeline())

    clusters = [
        SemanticCluster(
            label="Bloco 1",
            text="Equipe decidiu pela entrega incremental.",
            chunks=[
                SemanticChunk(
                    text="Equipe decidiu pela entrega incremental.",
                    start_time=0.0,
                    end_time=5.0,
                    token_start=0,
                    token_end=6,
                    embedding=np.ones(4, dtype=float),
                )
            ],
            start_time=0.0,
            end_time=5.0,
        )
    ]

    summary = service.generate_structured_summary("Texto completo da reunião.", clusters)

    assert summary["decisions"], "Lista de decisões não deve ficar vazia."
    assert summary["pending"], "Lista de pendências não deve ficar vazia."
    assert summary["next_steps"], "Lista de próximos passos não deve ficar vazia."
    assert summary["overview"], "Visão geral deve conter pelo menos um item."
