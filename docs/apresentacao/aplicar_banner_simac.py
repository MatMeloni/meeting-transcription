"""Aplica textos acadêmicos e figuras ao banner do VIII SIMAC, preservando o template."""
import copy, sys
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

FIG = "/home/user/meeting-transcription/docs/apresentacao/figuras/"
MUTED = RGBColor(0x5A, 0x65, 0x70)

prs = Presentation("base.pptx")
sl = prs.slides[0]
by_id = {sh.shape_id: sh for sh in sl.shapes}


def rewrite(tf, paragrafos):
    """Troca o texto preservando a formatação original de run e parágrafo."""
    modelo = next((r for pa in tf.paragraphs for r in pa.runs), None)
    rPr = copy.deepcopy(modelo._r.get_or_add_rPr()) if modelo is not None else None
    pPr = copy.deepcopy(tf.paragraphs[0]._p.get_or_add_pPr())
    tf.clear()
    for i, texto in enumerate(paragrafos):
        pa = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        antigo = pa._p.find(qn("a:pPr"))
        if antigo is not None:
            pa._p.remove(antigo)
        pa._p.insert(0, copy.deepcopy(pPr))
        if not texto:
            continue
        run = pa.add_run()
        run.text = texto
        if rPr is not None:
            r_el = run._r
            velho = r_el.find(qn("a:rPr"))
            if velho is not None:
                r_el.remove(velho)
            r_el.insert(0, copy.deepcopy(rPr))


def legenda(x, y, w, texto):
    cx = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.42))
    tf = cx.text_frame
    tf.word_wrap = True
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = texto
    r.font.name, r.font.size = "Arial", Pt(16)
    r.font.italic = True
    r.font.color.rgb = MUTED


# ------------------------------------------------- 0. correção do e-mail
for sh in sl.shapes:
    if not sh.has_text_frame:
        continue
    for pa in sh.text_frame.paragraphs:
        for r in pa.runs:
            if "gmail.com.br" in r.text or "Matheus.b.meloni" in r.text:
                r.text = r.text.replace("Matheus.b.meloni", "matheus.b.meloni")
                r.text = r.text.replace("gmail.com.br", "gmail.com")

# ------------------------------------------------- 1. título da faixa central
for sh in sl.shapes:
    if sh.shape_type == 6:
        for x in sh.shapes:
            if x.has_text_frame and "SOLUÇÃO" in x.text_frame.text:
                x.text_frame.paragraphs[0].runs[0].text = "FUNDAMENTAÇÃO E DISCUSSÃO"

# ----------------------------------------------------------- 2. textos ajustados
rewrite(by_id[25].text_frame, [
    "O estudo apoia-se em três fundamentos, articulados nas quatro camadas funcionais do "
    "pipeline (Figura 2). O primeiro é o reconhecimento de fala por arquiteturas "
    "codificador-decodificador baseadas em atenção (VASWANI et al., 2017), cujo treinamento por "
    "supervisão fraca confere robustez a ruído e variação de sotaque (RADFORD et al., 2022). "
    "O segundo é a representação distribuída de unidades linguísticas em espaços vetoriais "
    "contínuos, formulada por Mikolov et al. (2013) e estendida ao nível sentencial por Reimers "
    "e Gurevych (2019). O terceiro é a segmentação textual orientada por embeddings, que, "
    "conforme Alemi e Ginsparg (2015), produz fronteiras temáticas mais coerentes do que métodos "
    "fundados em recorrência lexical — o que converge com o limite de janelamento observado."
])

rewrite(by_id[19].text_frame, [
    "A instrumentação por etapa evidenciou que o custo computacional não se distribui "
    "uniformemente: concentra-se na transcrição e cresce linearmente com a duração do áudio, "
    "ao passo que a sumarização permanece aproximadamente constante, em decorrência do "
    "truncamento do contexto (Figura 1). Disso resulta comportamento não trivial do fator de "
    "tempo real, que melhora à medida que a duração aumenta — observação que relativiza a "
    "leitura usual de que registros mais longos seriam proporcionalmente mais custosos.",
    "",
    "Verificou-se, ainda, limite estrutural da segmentação: abaixo de determinada extensão "
    "textual, o janelamento produz uma única janela e o agrupamento não se efetiva. Trata-se de "
    "restrição derivada dos parâmetros adotados, e não do modelo de representação.",
    "",
    "A medição do pré-processamento foi obtida sobre o próprio pipeline; as demais etapas "
    "constituem projeção para a mesma classe de hardware.",
])

rewrite(by_id[29].text_frame, [
    "Os resultados sustentam a viabilidade da integração investigada e indicam que a principal "
    "limitação não reside no reconhecimento de fala, mas na etapa de sumarização, cujo modelo "
    "foi treinado majoritariamente em língua inglesa — a transcrição mostrou-se consistentemente "
    "superior ao resumo dela derivado.",
    "",
    "Reconhecem-se como limites o conjunto reduzido de registros, a avaliação por avaliador único "
    "e a restrição a captação em banda larga: registros de telefonia, confinados a 300–3.400 Hz, "
    "não foram contemplados, pois a reamostragem não restitui o conteúdo espectral ausente "
    "(Figura 3).",
    "",
    "Como desdobramentos, propõem-se sumarizador instruído em português, diarização de locutores, "
    "agrupamento com otimização global e avaliação sob banda estreita.",
])

rewrite(by_id[20].text_frame, [
    "ALEMI, A. A.; GINSPARG, P. Text Segmentation Based on Semantic Word Embeddings. "
    "arXiv:1503.05543, 2015.",
    "MIKOLOV, T. et al. Efficient Estimation of Word Representations in Vector Space. "
    "arXiv:1301.3781, 2013.",
    "RADFORD, A. et al. Robust Speech Recognition via Large-Scale Weak Supervision. "
    "arXiv:2212.04356, 2022.",
    "RAFFEL, C. et al. Exploring the Limits of Transfer Learning with a Unified Text-to-Text "
    "Transformer. JMLR, v. 21, n. 140, 2020.",
    "REIMERS, N.; GUREVYCH, I. Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks. "
    "EMNLP, 2019.",
    "VASWANI, A. et al. Attention is All You Need. NeurIPS, 2017.",
])

# --------------------------------------------- 3. remove a tira antiga do pipeline
el = by_id[48]._element
el.getparent().remove(el)

# -------------------------------- 4. Figura 1 — custo (coluna esquerda da faixa)
sl.shapes.add_picture(FIG + "custo_por_etapa.png", Inches(1.25), Inches(32.70), width=Inches(9.94))
legenda(1.25, 37.10, 9.94,
        "Figura 1 — Custo de processamento por etapa em função da duração do áudio; "
        "a faixa indica a amplitude projetada. Fonte: autoria própria (2026).")

# --------------------- 5. Figura 2 — arquitetura (reduzida, coluna direita da faixa)
arq = by_id[33]
arq.width = Inches(6.40)
arq.height = Inches(6.40 * 2464 / 2072)
arq.left = Inches(14.36)
arq.top = Inches(26.80)
legenda(12.40, 34.47, 9.30,
        "Figura 2 — Arquitetura em quatro camadas funcionais. Fonte: autoria própria (2026).")

# --------------------------------------------- 6. Figura 3 — banda telefônica
sl.shapes.add_picture(FIG + "banda_telefonica.png", Inches(12.40), Inches(35.15), width=Inches(9.30))
legenda(12.40, 37.72, 9.30,
        "Figura 3 — Cobertura espectral da banda telefônica frente à banda esperada pelo "
        "reconhecedor. Fonte: autoria própria (2026).")

prs.save(sys.argv[1])
print("gerado:", sys.argv[1])
