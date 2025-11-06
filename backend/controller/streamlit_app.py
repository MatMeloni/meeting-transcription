from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from backend.controller.pipeline_controller import PipelineController


def running_inside_streamlit() -> bool:
    """Detects whether the script is running under Streamlit."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx  # type: ignore

        return get_script_run_ctx() is not None
    except Exception:
        return False


def render_streamlit_app(controller: PipelineController) -> None:
    """Initializes the Streamlit interface for real-time monitoring."""
    import streamlit as st

    st.set_page_config(page_title="Transcrição Inteligente de Reuniões", layout="wide")
    st.title("Transcrição Inteligente de Reuniões")
    st.caption("Whisper + Sentence-BERT + T5 (pipeline modular)")

    meeting_name = st.text_input("Nome da reunião", value=controller.config.default_meeting_name)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            "Envie um arquivo de áudio (.wav, .mp3, .m4a)",
            type=["wav", "mp3", "m4a"],
        )
    with col2:
        duration = st.number_input(
            "Capturar áudio do microfone (segundos)",
            min_value=5,
            max_value=600,
            value=30,
            step=5,
        )
        capture_clicked = st.button("Capturar microfone agora")

    if capture_clicked:
        try:
            with st.spinner("Capturando áudio do microfone..."):
                result = controller.capture_and_process(duration, meeting_name=meeting_name)
            _render_streamlit_result(st, result)
        except Exception as exc:  # pragma: no cover - depende de hardware
            st.error(f"Falha durante a captura ao vivo: {exc}")

    if uploaded_file is not None:
        payload = uploaded_file.getbuffer().tobytes()
        with st.spinner("Processando arquivo enviado..."):
            result = controller.process_uploaded_bytes(
                payload=payload,
                original_filename=uploaded_file.name or "upload.wav",
                meeting_name=meeting_name,
            )
        _render_streamlit_result(st, result)

    sample_audio = controller.resolve_sample_audio()
    if sample_audio and sample_audio.exists():
        if st.button("Rodar pipeline com áudio de demonstração"):
            with st.spinner("Processando áudio de demonstração..."):
                result = controller.process_audio_file(
                    sample_audio, meeting_name=f"{meeting_name}_demo"
                )
            _render_streamlit_result(st, result)


def _render_streamlit_result(st_module, result: Dict[str, Any]) -> None:
    """Renders pipeline results inside Streamlit widgets."""
    st_module.success("Processamento concluído!")
    summary_tab, transcript_tab, export_tab = st_module.tabs(["Resumo", "Transcrição", "Exportações"])

    with summary_tab:
        st_module.subheader("Resumo Estruturado")
        summary = result["summary"]
        st_module.markdown("**Decisões**")
        for item in summary.get("decisions", []):
            st_module.markdown(f"- {item}")
        st_module.markdown("**Pendências**")
        for item in summary.get("pending", []):
            st_module.markdown(f"- {item}")
        st_module.markdown("**Próximos passos**")
        for item in summary.get("next_steps", []):
            st_module.markdown(f"- {item}")
        if overview := summary.get("overview"):
            st_module.markdown("**Visão geral**")
            for paragraph in overview:
                st_module.write(paragraph)

    with transcript_tab:
        st_module.subheader("Transcrição com timestamps")
        for segment in result.get("segments", []):
            st_module.markdown(f"**[{segment['start']:.2f}s – {segment['end']:.2f}s]** {segment['text']}")

    with export_tab:
        st_module.subheader("Downloads gerados")
        exports = result.get("exports", {})
        for export_group, files in exports.items():
            st_module.markdown(f"**{export_group.capitalize()}**")
            for fmt, path_str in files.items():
                export_path = Path(path_str)
                if export_path.exists():
                    data = export_path.read_bytes()
                    st_module.download_button(
                        label=f"Baixar {export_group} ({fmt.upper()})",
                        data=data,
                        file_name=export_path.name,
                        mime=(
                            "application/pdf"
                            if export_path.suffix.lower() == ".pdf"
                            else (
                                "application/json"
                                if export_path.suffix.lower() == ".json"
                                else "text/plain"
                            )
                        ),
                    )
                else:
                    st_module.warning(f"Arquivo não encontrado: {export_path}")

    st_module.caption(f"Reunião: {result['meeting_name']} | Gerado em: {result['timestamp']}")
