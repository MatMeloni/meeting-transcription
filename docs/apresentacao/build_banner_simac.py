"""Gera o banner do VIII SIMAC (Simpósio Acadêmico — Faculdade Eng. Salvador Arena).

Uso:
    python docs/apresentacao/build_banner_simac.py --output docs/apresentacao/BANNER_VIII_SIMAC_Meloni.pptx

Mantém a moldura oficial do evento (cabeçalho e rodapé, em figuras/simac_viii_fundo.jpg)
e monta o conteúdo em duas colunas, com cada seção fechada dentro de uma coluna —
sem a quebra de ordem de leitura e sem as colisões de texto do modelo de referência.

Dimensões: 22,835 x 47,245 pol (58 x 120 cm), escala 1:1 — 1 pt no arquivo = 1 pt impresso.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

FIG_DIR = Path(__file__).resolve().parent / "figuras"

# ---------------------------------------------------------------- identidade
AZUL = RGBColor(0x00, 0x5A, 0xAB)      # azul institucional do VIII SIMAC
INK = RGBColor(0x1A, 0x1A, 0x1A)
SOFT = RGBColor(0x4A, 0x55, 0x60)
FONT = "Arial"

# ------------------------------------------------------------------ geometria
W, H = Inches(22.835), Inches(47.245)
MARGEM = 0.80
GUTTER = 0.70
COL_W = (22.835 - 2 * MARGEM - GUTTER) / 2      # 10.2675 pol
COL_L = MARGEM                                   # x da coluna esquerda
COL_R = MARGEM + COL_W + GUTTER                  # x da coluna direita
TOPO, BASE = 10.30, 43.90                        # área livre entre cabeçalho e rodapé

# --------------------------------------------------------------- tipos de texto
TAM = {"titulo": 62, "autores": 25, "secao": 44, "sub": 33, "corpo": 28, "nota": 20, "ref": 20}


def altura(paragrafos, size, w, *, line=1.05, space_after=12, pad=0.10, fator=0.53):
    """Estima a altura necessária (pol) para os parágrafos na largura w (pol).

    Arial em texto justificado: largura média de caractere ~0,53 em (use fator
    ~0,64 para caixa-alta em negrito, bem mais larga); altura de
    linha = corpo x 1,2 x entrelinha. Mede-se antes de posicionar para que
    nenhuma seção invada a seguinte.
    """
    largura_pt = w * 72 - 6
    por_linha = max(1, int(largura_pt / (fator * size)))
    altura_linha = size * 1.2 * line
    total_pt = 0.0
    for texto in paragrafos:
        linhas = max(1, -(-len(texto) // por_linha))
        total_pt += linhas * altura_linha + space_after
    return total_pt / 72 + pad


def caixa(slide, x, y, w, h):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    tf.clear()
    return tf


def par(tf, texto, *, size, bold=False, italic=False, color=INK,
        align=PP_ALIGN.JUSTIFY, space_after=10, space_before=0, first=False,
        line=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    if line:
        p.line_spacing = line
    run = p.add_run()
    run.text = texto
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return p


def secao(slide, x, y, titulo, *, w=COL_W):
    """Título de seção, com a régua azul por baixo."""
    tf = caixa(slide, x, y, w, 0.95)
    par(tf, titulo, size=TAM["secao"], bold=True, color=AZUL,
        align=PP_ALIGN.LEFT, space_after=0, first=True)
    linha = slide.shapes.add_shape(1, Inches(x), Inches(y + 0.88), Inches(w), Inches(0.035))
    linha.fill.solid()
    linha.fill.fore_color.rgb = AZUL
    linha.line.fill.background()
    linha.shadow.inherit = False
    return y + 1.08


def bloco(slide, x, y, paragrafos, *, size=None, w=COL_W, align=PP_ALIGN.JUSTIFY):
    """Escreve o bloco numa caixa do tamanho medido e devolve o y seguinte."""
    size = size or TAM["corpo"]
    h = altura(paragrafos, size, w)
    tf = caixa(slide, x, y, w, h)
    for i, texto in enumerate(paragrafos):
        par(tf, texto, size=size, first=(i == 0), space_after=12, line=1.05, align=align)
    return y + h


# --------------------------------------------------------------------- conteúdo
TITULO = ("AUTOMAÇÃO DE TRANSCRIÇÃO E ANÁLISE DE REUNIÕES "
          "UTILIZANDO INTELIGÊNCIA ARTIFICIAL")

AUTORES = [
    "Matheus Barbosa Meloni, matheus.b.meloni@gmail.com, Universidade Presbiteriana Mackenzie",
    "Victor Inácio de Oliveira, victor.inacio@mackenzie.br, Universidade Presbiteriana Mackenzie",
]

INTRODUCAO = [
    "Reuniões concentram decisões, pendências e encaminhamentos, mas o registro depende de "
    "anotação manual: é custoso, parcial e raramente rastreável ao que foi efetivamente dito.",

    "O avanço do Reconhecimento Automático de Fala e do Processamento de Linguagem Natural "
    "tornou viável automatizar esse registro: o Whisper transcreve com robustez mesmo sob ruído "
    "(RADFORD et al., 2022) e a segmentação por embeddings supera métodos baseados em "
    "palavras-chave (ALEMI; GINSPARG, 2015).",

    "As soluções comerciais equivalentes são proprietárias, orientadas ao inglês e dependentes "
    "de nuvem, o que impede auditar o processo e impõe restrições de privacidade sobre o áudio.",
]

OBJETIVO_GERAL = [
    "Desenvolver um sistema modular, reprodutível e executável localmente que converta áudio de "
    "reuniões em português em documentação acionável: decisões, pendências e próximos passos.",
]

OBJETIVOS_ESPECIFICOS = [
    "•  Integrar transcrição automática, estruturação semântica por embeddings e sumarização "
    "em um pipeline único e instrumentado.",
    "•  Isolar o núcleo de IA das camadas de uso — linha de comando, API e interface web —, "
    "tornando-o reutilizável e testável.",
    "•  Instrumentar o desempenho por etapa e avaliar o sistema sob protocolo reprodutível.",
]

METODOLOGIA = [
    "Pipeline modular de cinco estágios, cada um com responsabilidade única e saída definida "
    "para o seguinte.",

    "1. Pré-processamento: remoção de silêncio, normalização de pico, subtração espectral em "
    "blocos de 60 s e reamostragem para 16 kHz mono.",

    "2. Transcrição (faster-whisper): busca em feixe (beam_size = 5), filtro de atividade de voz "
    "e idioma fixado em português, com marcação temporal por segmento.",

    "3. Estruturação semântica (Sentence-BERT): janelas de 500 tokens com sobreposição de 50, "
    "convertidas em vetores normalizados.",

    "4. Agrupamento: similaridade de cosseno contra limiar de 0,78, com os blocos remapeados ao "
    "eixo temporal.",

    "5. Sumarização (T5): três instruções fixas — decisões, pendências e próximos passos.",

    "A configuração é externalizada em variáveis de ambiente: cada rodada experimental é "
    "descrita por parâmetros, não por alteração de código.",
]

RESULTADOS = [
    "O pipeline está operacional de ponta a ponta, acessível por linha de comando, API REST e "
    "interface web. Cada execução exporta a transcrição com marcação temporal e o resumo "
    "estruturado em PDF e JSON, permitindo rastrear cada item do resumo até o minuto do áudio.",

    "A instrumentação por etapa mostrou que o custo é dominado pela transcrição e cresce "
    "linearmente com a duração, enquanto a sumarização permanece constante, por ter o contexto "
    "limitado a 300 tokens. Assim, o fator de tempo real (RTF) melhora conforme a reunião "
    "cresce: de 0,41–0,78 em 2 min para 0,21–0,45 em 10 min.",
]

RESULTADOS_NOTA = (
    "Pré-processamento medido sobre o próprio pipeline (CPU x86-64, 4 núcleos, sem GPU); "
    "demais etapas projetadas para a mesma classe de hardware."
)

CONSIDERACOES = [
    "O objetivo foi atingido no nível de sistema: há um pipeline reprodutível que converte áudio "
    "de reunião em documentação estruturada e rastreável ao tempo do áudio.",

    "O gargalo de qualidade está na sumarização, que emprega um modelo pequeno treinado "
    "majoritariamente em inglês. Os próximos passos são um sumarizador instruído em português, "
    "diarização de falantes e avaliação com WER/CER sobre corpus anotado.",
]

REFERENCIAS = [
    "ALEMI, A. A.; GINSPARG, P. Text segmentation based on semantic word embeddings. "
    "arXiv:1503.05543, 2015.",
    "RADFORD, A. et al. Robust speech recognition via large-scale weak supervision. "
    "arXiv:2212.04356, 2022.",
    "RAFFEL, C. et al. Exploring the limits of transfer learning with a unified text-to-text "
    "transformer. Journal of Machine Learning Research, v. 21, n. 140, p. 1-67, 2020.",
    "REIMERS, N.; GUREVYCH, I. Sentence-BERT: sentence embeddings using Siamese BERT-networks. "
    "In: EMNLP-IJCNLP, 2019. p. 3982-3992.",
]



def montar(prs, corpo_pt: int):
    """Monta o banner com o corpo no tamanho dado; devolve o fim de cada coluna."""
    for sld in list(prs.slides._sldIdLst):
        prs.slides._sldIdLst.remove(sld)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # moldura oficial do evento, em sangria total
    slide.shapes.add_picture(str(FIG_DIR / "simac_viii_fundo.jpg"), 0, 0, width=W, height=H)

    larg = 22.835 - 2 * MARGEM
    larg_tit = 22.835 - 2 * 0.40

    # ------------------------------------------------------------ cabeçalho
    h_tit = altura([TITULO], TAM["titulo"], larg_tit, line=0.95, space_after=0,
                   pad=0.22, fator=0.64)
    tf = caixa(slide, 0.40, TOPO, larg_tit, h_tit)
    par(tf, TITULO, size=TAM["titulo"], bold=True, color=AZUL,
        align=PP_ALIGN.CENTER, space_after=0, first=True, line=0.95)

    y = TOPO + h_tit + 0.28
    h_aut = altura(AUTORES, TAM["autores"], larg, line=1.0, space_after=4, pad=0.10)
    tf = caixa(slide, MARGEM, y, larg, h_aut)
    for i, autor in enumerate(AUTORES):
        par(tf, autor, size=TAM["autores"], color=INK,
            align=PP_ALIGN.CENTER, space_after=4, first=(i == 0))

    y0 = y + h_aut + 0.55

    # ------------------------------------------------------- coluna esquerda
    y = secao(slide, COL_L, y0, "Introdução")
    y = bloco(slide, COL_L, y, INTRODUCAO, size=corpo_pt)

    y = secao(slide, COL_L, y + 0.38, "Objetivos")
    tf = caixa(slide, COL_L, y, COL_W, 0.70)
    par(tf, "Objetivo geral", size=TAM["sub"], bold=True, italic=True, color=SOFT,
        align=PP_ALIGN.LEFT, space_after=0, first=True)
    y = bloco(slide, COL_L, y + 0.74, OBJETIVO_GERAL, size=corpo_pt)

    tf = caixa(slide, COL_L, y + 0.22, COL_W, 0.70)
    par(tf, "Objetivos específicos", size=TAM["sub"], bold=True, italic=True, color=SOFT,
        align=PP_ALIGN.LEFT, space_after=0, first=True)
    y = bloco(slide, COL_L, y + 0.96, OBJETIVOS_ESPECIFICOS, size=corpo_pt,
              align=PP_ALIGN.LEFT)

    y = secao(slide, COL_L, y + 0.38, "Metodologia")
    y = bloco(slide, COL_L, y, METODOLOGIA, size=corpo_pt)
    fim_esq = y

    # --------------------------------------------------------- coluna direita
    y = secao(slide, COL_R, y0, "Resultados preliminares")
    y = bloco(slide, COL_R, y, RESULTADOS, size=corpo_pt)

    h_nota = altura([RESULTADOS_NOTA], TAM["nota"], COL_W, line=1.05, space_after=0, pad=0.08)
    tf = caixa(slide, COL_R, y + 0.10, COL_W, h_nota)
    par(tf, RESULTADOS_NOTA, size=TAM["nota"], italic=True, color=SOFT,
        align=PP_ALIGN.LEFT, space_after=0, first=True, line=1.05)
    y = y + 0.10 + h_nota

    fig_w = 7.20
    fig_x = COL_R + (COL_W - fig_w) / 2
    fig_y = y + 0.45
    pic = slide.shapes.add_picture(str(FIG_DIR / "arquitetura_camadas.png"),
                                   Inches(fig_x), Inches(fig_y), width=Inches(fig_w))
    y = fig_y + Emu(pic.height).inches + 0.16

    legenda = "Figura 1 — Arquitetura em quatro camadas funcionais. Fonte: autoria própria (2026)."
    h_leg = altura([legenda], TAM["nota"], COL_W, line=1.0, space_after=0, pad=0.08)
    tf = caixa(slide, COL_R, y, COL_W, h_leg)
    par(tf, legenda, size=TAM["nota"], italic=True, color=SOFT,
        align=PP_ALIGN.CENTER, space_after=0, first=True)
    y += h_leg

    y = secao(slide, COL_R, y + 0.40, "Considerações finais")
    y = bloco(slide, COL_R, y, CONSIDERACOES, size=corpo_pt)

    y = secao(slide, COL_R, y + 0.38, "Referências")
    h_ref = altura(REFERENCIAS, TAM["ref"], COL_W, line=1.0, space_after=9, pad=0.10)
    tf = caixa(slide, COL_R, y, COL_W, h_ref)
    for i, ref in enumerate(REFERENCIAS):
        par(tf, ref, size=TAM["ref"], color=INK, space_after=9, first=(i == 0), line=1.0)
    fim_dir = y + h_ref

    return fim_esq, fim_dir


def build(output: Path) -> None:
    """Monta o banner com o maior corpo de texto que couber nas duas colunas."""
    for corpo_pt in (28, 27, 26, 25, 24, 23, 22):
        prs = Presentation()
        prs.slide_width, prs.slide_height = W, H
        fim_esq, fim_dir = montar(prs, corpo_pt)
        if max(fim_esq, fim_dir) <= BASE:
            print(f"corpo = {corpo_pt} pt | coluna esq. termina em {fim_esq:.2f}\" | "
                  f"dir. em {fim_dir:.2f}\" | limite {BASE}\"")
            output.parent.mkdir(parents=True, exist_ok=True)
            prs.save(str(output))
            print(f"Banner gerado: {output}")
            return
        print(f"corpo = {corpo_pt} pt não coube (esq. {fim_esq:.2f}\", dir. {fim_dir:.2f}\") — reduzindo")
    raise SystemExit("Conteúdo longo demais para a área útil: encurte os textos.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    build(ap.parse_args().output)


if __name__ == "__main__":
    main()
