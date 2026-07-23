from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from config import AppConfig
from utils.text_utils import approximate_token_count


class ExportService:
    """Exports transcripts and summaries to PDF, TXT and JSON formats."""

    def __init__(self, config: AppConfig):
        self.config = config

    def export_transcript(
        self, transcript_text: str, transcript_path: Path, metadata: Dict[str, str]
    ) -> Dict[str, Path]:
        """Generates a PDF version of the transcript alongside the TXT file."""
        pdf_path = transcript_path.with_suffix(".pdf")
        self._write_pdf(pdf_path, "Transcrição Completa", transcript_text, metadata)
        return {
            "txt": transcript_path,
            "pdf": pdf_path,
        }

    def export_summary(
        self, summary: Dict[str, List[str]], metadata: Dict[str, str]
    ) -> Dict[str, Path]:
        """Exports the structured summary to PDF and JSON outputs."""
        filename = f"{metadata['meeting_name']}_{metadata['timestamp']}_resumo"
        pdf_path = self.config.summaries_dir / f"{filename}.pdf"
        json_path = self.config.summaries_dir / f"{filename}.json"

        pdf_content = self._format_summary_for_pdf(summary)
        self._write_pdf(pdf_path, "Resumo Automático da Reunião", pdf_content, metadata)

        json_payload = {
            "metadata": metadata,
            "summary": summary,
        }
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(json_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logging.info("Resumo exportado em %s e %s", pdf_path, json_path)
        return {"pdf": pdf_path, "json": json_path}

    def _write_pdf(
        self, path: Path, title: str, body_text: str, metadata: Dict[str, str]
    ) -> None:
        """Creates a simple PDF document with metadata header and body text."""
        path.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Gerando PDF em %s...", path)
        pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        margin = 40
        y_position = height - margin

        pdf_canvas.setFont("Helvetica-Bold", 16)
        pdf_canvas.drawString(margin, y_position, title)
        y_position -= 24

        pdf_canvas.setFont("Helvetica", 10)
        token_count = approximate_token_count(body_text)
        meta_line = (
            f"Reunião: {metadata['meeting_name']} | Gerado em: {metadata['timestamp']} | Tokens ~ {token_count}"
        )
        pdf_canvas.drawString(margin, y_position, meta_line)
        y_position -= 18

        pdf_canvas.setFont("Helvetica", 11)
        max_width = width - (2 * margin)
        for line in body_text.split("\n"):
            wrapped = self._wrap_line(line, max_width, pdf_canvas, "Helvetica", 11)
            for chunk in wrapped:
                if y_position <= margin:
                    pdf_canvas.showPage()
                    y_position = height - margin
                    pdf_canvas.setFont("Helvetica", 11)
                pdf_canvas.drawString(margin, y_position, chunk)
                y_position -= 14

        pdf_canvas.save()
        logging.info("PDF finalizado em %s", path)

    @staticmethod
    def _wrap_line(
        text: str, max_width: float, pdf_canvas, font_name: str, font_size: int
    ) -> List[str]:
        """Wraps a single line of text to fit the PDF page width."""
        if not text:
            return [""]
        words = text.split(" ")
        lines: List[str] = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if pdf_canvas.stringWidth(candidate, font_name, font_size) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
        if current:
            lines.append(current)
        return lines or [""]

    def _format_summary_for_pdf(self, summary: Dict[str, List[str]]) -> str:
        """Formats structured summary sections into printable text."""
        lines = []
        for section, items in summary.items():
            section_title = {
                "decisions": "Decisões",
                "pending": "Pendências",
                "next_steps": "Próximos passos",
                "overview": "Visão geral",
            }.get(section, section.capitalize())
            lines.append(f"{section_title}:")
            if items:
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append("- (sem itens)")
            lines.append("")
        return "\n".join(lines).strip()
