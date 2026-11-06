"""Gera a apresentação da XXII Jornada de Iniciação Científica (Mackenzie, 2026)
a partir do template oficial "Pesquisa de Campo" enviado pelo CFP.

Uso:
    python docs/apresentacao/build_apresentacao.py \
        --template docs/apresentacao/template/2026_PESQUISA_DE_CAMPO.pptx \
        --output docs/apresentacao/APRESENTACAO_JIC_2026_Meloni.pptx

O script preserva integralmente a identidade visual do template (fundos,
logotipos, traços) e apenas insere caixas de texto na área útil de cada slide.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# --------------------------------------------------------------------------- #
# Identidade visual extraída do próprio template
# --------------------------------------------------------------------------- #
ACCENT = RGBColor(0xE4, 0x18, 0x4B)   # rosa/vermelho institucional
INK = RGBColor(0x11, 0x1A, 0x24)      # texto sobre fundo claro
INK_SOFT = RGBColor(0x3C, 0x48, 0x55)  # texto secundário
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

# Área útil dos slides de conteúdo (evita logo superior esquerdo,
# traço rosa à direita e logo Mackenzie inferior direito)
BODY_LEFT = Inches(0.55)
BODY_TOP = Inches(1.10)
BODY_WIDTH = Inches(10.45)
BODY_HEIGHT = Inches(5.25)
FIG_DIR = Path(__file__).resolve().parent / "figuras"
CONTENT_TOP = Inches(1.62)   # abaixo do subtítulo de seção


# --------------------------------------------------------------------------- #
# Infraestrutura
# --------------------------------------------------------------------------- #
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def duplicate_slide(prs: Presentation, index: int):
    """Duplica o slide `index` (inclusive imagens de fundo) ao final do deck.

    python-pptx não expõe duplicação nativa: copia-se o XML das formas e
    recriam-se as relações da parte (imagens), remapeando os rIds no XML
    copiado para os rIds atribuídos no slide de destino.
    """
    source = prs.slides[index]
    dest = prs.slides.add_slide(source.slide_layout)

    # O layout insere placeholders vazios; removê-los antes de copiar
    for shape in list(dest.shapes):
        shape._element.getparent().remove(shape._element)

    rid_map: dict[str, str] = {}
    for rid, rel in source.part.rels.items():
        if rel.reltype.endswith("slideLayout"):
            continue
        rid_map[rid] = dest.part.rels._add_relationship(
            rel.reltype, rel._target, rel.is_external
        )

    for shape in source.shapes:
        element = copy.deepcopy(shape._element)
        for node in element.iter():
            for attr, value in list(node.attrib.items()):
                if attr.startswith("{%s}" % R_NS) and value in rid_map:
                    node.attrib[attr] = rid_map[value]
        dest.shapes._spTree.append(element)

    return dest


def reorder(prs: Presentation, order: list[int]) -> None:
    """Reordena os slides conforme a lista de índices originais."""
    sld_id_lst = prs.slides._sldIdLst
    ids = list(sld_id_lst)
    for element in ids:
        sld_id_lst.remove(element)
    for i in order:
        sld_id_lst.append(ids[i])


def find_shape(slide, name: str):
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    return None


def set_title(slide, text: str, size: int = 24) -> None:
    """Reescreve o título da seção mantendo-o centralizado no slide."""
    shape = find_shape(slide, "Título 1")
    if shape is None:
        return
    shape.left, shape.width = Inches(2.0), Inches(9.33)
    tf = shape.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = INK


def add_box(slide, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    return tf


def write(tf, blocks, first=True):
    """Escreve blocos (kind, texto) num text frame.

    kinds: 'h'  subtítulo de seção (rosa, negrito)
           'b'  bullet de 1º nível
           's'  bullet de 2º nível
           'n'  nota/observação em itálico
           'p'  parágrafo corrido
    """
    for kind, text in blocks:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False

        if kind == "h":
            p.space_before, p.space_after = Pt(10), Pt(4)
            run = p.add_run()
            run.text = text
            run.font.bold = True
            run.font.size = Pt(16)
            run.font.color.rgb = ACCENT
        elif kind == "b":
            p.space_before, p.space_after = Pt(5), Pt(1)
            _indent(p, Inches(0.22), Inches(-0.22))
            run = p.add_run()
            run.text = text if text[:2].strip().rstrip(".").isdigit() else "\u25aa\u2002" + text
            run.font.size = Pt(15)
            run.font.color.rgb = INK
        elif kind == "s":
            p.space_before, p.space_after = Pt(2), Pt(1)
            _indent(p, Inches(0.52), Inches(-0.19))
            run = p.add_run()
            run.text = "\u2013\u2002" + text
            run.font.size = Pt(13.5)
            run.font.color.rgb = INK_SOFT
        elif kind == "n":
            p.space_before, p.space_after = Pt(8), Pt(0)
            run = p.add_run()
            run.text = text
            run.font.size = Pt(12.5)
            run.font.italic = True
            run.font.color.rgb = INK_SOFT
        else:  # 'p'
            p.space_before, p.space_after = Pt(3), Pt(2)
            run = p.add_run()
            run.text = text
            run.font.size = Pt(14.5)
            run.font.color.rgb = INK

        for r in p.runs:
            r.font.name = FONT
    return tf


def _indent(paragraph, mar_left, hanging) -> None:
    """Define recuo com marcador pendurado (python-pptx não expõe a API)."""
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("marL", str(int(mar_left)))
    pPr.set("indent", str(int(hanging)))


def add_table(slide, left, top, width, headers, rows, col_widths=None,
              row_height=0.32, font_size=11, emphasis_rows=()):
    """Insere uma tabela formatada com a identidade visual do template."""
    n_rows, n_cols = len(rows) + 1, len(headers)
    height = Inches(row_height) * n_rows
    table = slide.shapes.add_table(n_rows, n_cols, left, top, width, height).table

    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w

    for j, header in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = Inches(0.05)
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        for run in para.runs:
            run.font.name, run.font.size = FONT, Pt(font_size)
            run.font.bold = True
            run.font.color.rgb = WHITE

    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(value)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFD, 0xE8, 0xED) if i in emphasis_rows
                else RGBColor(0xFF, 0xFF, 0xFF) if i % 2
                else RGBColor(0xF2, 0xF4, 0xF6)
            )
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.05)
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT if j in (0, n_cols - 1) else PP_ALIGN.CENTER
            for run in para.runs:
                run.font.name, run.font.size = FONT, Pt(font_size)
                run.font.bold = i in emphasis_rows
                run.font.color.rgb = ACCENT if i in emphasis_rows else INK
    return table


def add_pipeline_diagram(slide, left, top, stages) -> None:
    """Desenha o fluxo do pipeline como uma sequência de chevrons encadeados."""
    width, step, height = Inches(1.80), Inches(1.65), Inches(0.62)
    for i, (rotulo, destaque) in enumerate(stages):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.CHEVRON, left + step * i, top, width, height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = ACCENT if destaque else INK
        shape.line.color.rgb = WHITE
        shape.line.width = Pt(1.0)
        shape.shadow.inherit = False

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.04)
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        run = para.add_run()
        run.text = rotulo
        run.font.name, run.font.size = FONT, Pt(9)
        run.font.bold = True
        run.font.color.rgb = WHITE


def notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text.strip()


# --------------------------------------------------------------------------- #
# Conteúdo
# --------------------------------------------------------------------------- #
TITULO = "AUTOMAÇÃO DE TRANSCRIÇÃO E ANÁLISE DE REUNIÕES UTILIZANDO INTELIGÊNCIA ARTIFICIAL"
ALUNO = "Matheus Barbosa Meloni"
ORIENTADOR = "Prof. Victor Inácio de Oliveira"


def build(template: Path, output: Path) -> None:
    prs = Presentation(str(template))

    # Template original: 0 capa | 1 título | 2 introdução | 3 metodologia
    #                    4 resultados | 5 considerações | 6 referências | 7 agradecimentos
    met2 = duplicate_slide(prs, 3)   # índice 8
    res2 = duplicate_slide(prs, 4)   # índice 9
    res3 = duplicate_slide(prs, 4)   # índice 10
    reorder(prs, [0, 1, 2, 3, 8, 4, 9, 10, 5, 6, 7])

    s = prs.slides

    # ---------------------------------------------------------------- slide 2
    caixa = find_shape(s[1], "CaixaDeTexto 3")
    caixa.left, caixa.top = Inches(4.35), Inches(1.15)
    caixa.width, caixa.height = Inches(8.55), Inches(4.20)
    tf = caixa.text_frame
    tf.word_wrap = True
    tf.clear()

    linhas = [
        (TITULO, 19, True, WHITE, 14),
        ("Matheus Barbosa Meloni  —  aluno pesquisador", 14, False, WHITE, 6),
        ("Prof. Victor Inácio de Oliveira  —  orientador", 14, False, WHITE, 14),
        ("Escola de Engenharia  |  Engenharia da Computação  |  Campus Higienópolis", 12, False, WHITE, 4),
        ("Programa de Iniciação Científica (PIBIC/PIVIC) 2025–2026", 12, False, WHITE, 4),
        ("Apoio institucional: Universidade Presbiteriana Mackenzie / CNPq", 12, False, WHITE, 0),
    ]
    for i, (texto, size, bold, color, space_after) in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(space_after)
        run = p.add_run()
        run.text = texto
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color

    notes(s[1], """
ABERTURA (0:00–0:45). Cumprimentar a banca. Dizer título, seu nome e o do orientador.
Frase de gancho: "Toda reunião produz decisões, mas quase nenhuma produz um registro
confiável dessas decisões. Este trabalho ataca exatamente essa lacuna."
Anunciar o roteiro: problema, método, resultados, limitações e próximos passos.
""")

    # ---------------------------------------------------------------- slide 3
    set_title(s[2], "INTRODUÇÃO", 24)
    tf = add_box(s[2], BODY_LEFT, BODY_TOP, BODY_WIDTH, BODY_HEIGHT)
    write(tf, [
        ("h", "Problema"),
        ("p", "O registro documental de reuniões sustenta a rastreabilidade de decisões em contextos "
              "acadêmicos e organizacionais. Conduzido manualmente, é oneroso, seletivo e dependente "
              "da interpretação do anotador, o que compromete sua fidedignidade em relação ao que foi "
              "efetivamente enunciado."),
        ("h", "Fundamentos disponíveis"),
        ("s", "Reconhecimento de fala robusto sob ruído (RADFORD et al., 2022)."),
        ("s", "Representação semântica distribuída em nível sentencial (REIMERS; GUREVYCH, 2019)."),
        ("s", "Segmentação textual orientada por embeddings (ALEMI; GINSPARG, 2015)."),
        ("h", "Lacuna"),
        ("p", "Tais recursos têm sido investigados de forma isolada. Permanece em aberto o "
              "comportamento do encadeamento aplicado ao português brasileiro — tanto na distribuição "
              "do custo computacional quanto na preservação da correspondência entre o resumo "
              "produzido e o trecho de áudio que o originou."),
        ("h", "Pergunta de pesquisa"),
        ("p", "De que modo a integração entre reconhecimento de fala, representação semântica "
              "distribuída e sumarização neural produz documentação estruturada e rastreável de "
              "reuniões em português, e como o custo computacional se distribui entre as etapas?"),
        ("h", "Objetivo geral"),
        ("p", "Investigar a viabilidade dessa integração, caracterizando o comportamento do pipeline "
              "no processamento de registros orais de reuniões em português."),
    ])
    notes(s[2], """
INTRODUÇÃO (0:45–3:05). Não leia os blocos.
1) Problema (40s): a ata manual é o gargalo; o que se perde não é o áudio, é a decisão.
2) Fundamentos (35s): três famílias de modelos maduras, até então usadas isoladamente.
3) Lacuna (35s): o encadeamento em português não está caracterizado — nem o custo, nem a
   rastreabilidade entre resumo e áudio.
4) Pergunta de pesquisa (20s): leia-a inteira, devagar. É o que converte isto em pesquisa.
5) Objetivo (20s): a frase que a banca vai cobrar no final.
Transição: "Para investigar isso, estruturei o trabalho como engenharia de pipeline instrumentado."
""")

    # ---------------------------------------------------------------- slide 4
    set_title(s[3], "METODOLOGIA", 24)
    tf = add_box(s[3], BODY_LEFT, Inches(1.02), BODY_WIDTH, Inches(0.40))
    write(tf, [("h", "Arquitetura do pipeline — cinco estágios encadeados")])

    tf = add_box(s[3], BODY_LEFT, Inches(1.50), BODY_WIDTH, Inches(3.15))
    write(tf, [
        ("b", "1.  Pré-processamento do sinal acústico — remoção de silêncio nas extremidades "
              "(top_db = 25), normalização de pico, subtração espectral em blocos de 60 s e "
              "reamostragem para 16 kHz mono."),
        ("b", "2.  Transcrição / ASR (faster-whisper) — decodificação por feixe (beam_size = 5), "
              "filtro de atividade de voz (VAD) e idioma fixado em pt; saída segmentada com "
              "marcação temporal."),
        ("b", "3.  Estruturação semântica (Sentence-BERT) — janelas deslizantes de 500 tokens com "
              "sobreposição de 50; cada janela vira um vetor normalizado em L2."),
        ("b", "4.  Agrupamento temático — similaridade de cosseno contra limiar de 0,78, com fusão "
              "incremental gulosa; cada bloco é remapeado ao eixo temporal da reunião."),
        ("b", "5.  Sumarização (T5-small local, ou API externa por configuração) — três instruções "
              "fixas: decisões, pendências e próximos passos, mais uma visão geral."),
    ])

    s[3].shapes.add_picture(
        str(FIG_DIR / "pipeline_horizontal.png"),
        BODY_LEFT, Inches(4.78), width=Inches(10.45),
    )
    tf = add_box(s[3], BODY_LEFT, Inches(6.28), BODY_WIDTH, Inches(0.32))
    write(tf, [("n", "Figura 1 — Fluxo de ponta a ponta do pipeline.")])

    notes(s[3], """
METODOLOGIA – PIPELINE (3:05–5:45). Este é o slide central: ande pelas cinco etapas.
Ancoragem: "A ideia é ir do sinal sonoro ao texto, do texto a tópicos, e de tópicos à decisão."
Aponte a Figura 1 com a mão enquanto percorre os estágios — ela carrega o fluxo, e o texto
carrega os parâmetros. Não leia os dois.
1) Pré-processamento (30s): lixo entra, lixo sai. Blocos de 60 s porque gravações longas
   estouravam a memória.
2) ASR (40s): beam search custa tempo mas reduz erro; VAD evita alucinação em silêncio;
   fixar pt evita troca espúria de idioma.
3) Embeddings (35s): a sobreposição evita cortar uma ideia ao meio.
4) Agrupamento (35s): cosseno com limiar 0,78; guloso, decisão consciente (volta nas limitações).
5) Sumarização (30s): o resumo não é livre, é guiado por três perguntas fixas. O sumarizador é
   CONFIGURÁVEL: T5 local, ou API externa — e essa escolha troca privacidade por qualidade.
>>> RESSALVA sobre a Figura 1: a caixa "Armazenar no Vetor DB" representa o desenho da arquitetura,
    não a implementação atual. No código os blocos e embeddings ficam em memória e os segmentos são
    persistidos em JSON em disco — não há banco vetorial. Se perguntarem qual banco vetorial você usa,
    responda: "nenhum ainda; o agrupamento é feito em NumPy sobre os vetores em memória, e o índice
    vetorial é o caminho previsto para escalar a busca."
Se o tempo apertar, resuma 1 e 5 e preserve 3 e 4 — é onde está a contribuição técnica.
""")

    # ---------------------------------------------------------------- slide 5
    set_title(s[4], "METODOLOGIA", 24)
    tf = add_box(s[4], BODY_LEFT, Inches(1.02), BODY_WIDTH, Inches(0.40))
    write(tf, [("h", "Arquitetura em camadas, reprodutibilidade e verificação")])

    s[4].shapes.add_picture(
        str(FIG_DIR / "arquitetura_camadas.png"),
        BODY_LEFT, Inches(1.44), height=Inches(4.92),
    )
    tf = add_box(s[4], BODY_LEFT, Inches(6.40), Inches(4.30), Inches(0.30))
    write(tf, [("n", "Figura 2 — As quatro camadas funcionais.")])

    tf = add_box(s[4], Inches(4.92), Inches(1.46), Inches(6.08), Inches(4.90))
    write(tf, [
        ("b", "Arquitetura em camadas — o núcleo de IA (src/) é independente das camadas de uso "
              "(linha de comando, API FastAPI, painel Streamlit, front-end Next.js) e pode ser "
              "testado sem subir interface."),
        ("b", "Configuração externalizada — modelo de ASR, embeddings, sumarizador, tamanho de "
              "janela, sobreposição e limiar de similaridade são variáveis de ambiente: uma rodada "
              "experimental é descrita por variáveis, não por alteração de código."),
        ("b", "Instrumentação — toda execução devolve stage_timings, com o tempo de cada etapa do "
              "pipeline e o tempo total de parede."),
        ("b", "Verificação — suíte automatizada em pytest com dublês de modelos: 15 testes em 6 "
              "módulos, cobrindo transcrição, embeddings, sumarização, upload, API e integração."),
        ("b", "Protocolo experimental — 2 a 4 cenários de áudio com perfis distintos; cada perfil "
              "estressa uma etapa diferente do pipeline."),
    ])

    notes(s[4], """
METODOLOGIA – RIGOR (5:45–7:35). Aqui você mostra método, não código.
Mensagem única: "As decisões de arquitetura foram tomadas para que o experimento fosse reprodutível."
A Figura 2 mostra as quatro camadas; use-a para dizer que o núcleo não sabe que existe interface.
1) Camadas (25s): o núcleo é independente das formas de acionamento.
2) Configuração externalizada (30s): argumento mais forte de rigor — outro pesquisador reproduz
   a rodada sem tocar no código.
3) Instrumentação (25s): sem medir por etapa não se sabe onde está o custo.
4) Testes (20s): dublês de modelos permitem testar a lógica sem baixar modelos pesados.
5) Protocolo (20s): os perfis de áudio não são arbitrários — cada um estressa uma etapa.
""")

    # ---------------------------------------------------------------- slide 6
    set_title(s[5], "RESULTADOS E DISCUSSÃO", 23)
    tf = add_box(s[5], BODY_LEFT, BODY_TOP, BODY_WIDTH, Inches(0.42))
    write(tf, [("h", "Entrega funcional: o que o sistema efetivamente faz")])
    tf = add_box(s[5], BODY_LEFT, CONTENT_TOP, BODY_WIDTH, Inches(4.75))
    write(tf, [
        ("b", "Pipeline integrado e operacional de ponta a ponta, acessível por três vias: linha de comando, "
              "API REST (GET /health, POST /transcribe) e painel Streamlit, além de front-end web."),
        ("b", "Saídas produzidas por execução:"),
        ("s", "transcrição com marcação temporal por segmento no formato [HH:MM:SS --> HH:MM:SS];"),
        ("s", "blocos semânticos rotulados, com intervalo de tempo aproximado na linha do tempo da reunião;"),
        ("s", "resumo em três seções — decisões, pendências e próximos passos — mais uma visão geral;"),
        ("s", "exportação em TXT, PDF e JSON, permitindo consumo humano e consumo por outro sistema."),
        ("b", "Robustez operacional: validação de upload (limite de 50 MiB e extensões .wav/.mp3/.m4a/"
              ".webm/.ogg), redução de ruído em blocos para gravações longas e empacotamento em Docker."),
        ("b", "Ferramentas de medição entregues: benchmark_pipeline.py agrega métricas de vários áudios em "
              "tabela; compare_whisper_models.py executa comparação A/B entre tamanhos de modelo."),
        ("n", "Discussão: a modularidade foi validada na prática — o agrupamento foi reimplementado em NumPy "
              "puro, eliminando a dependência de FAISS, sem qualquer alteração nas camadas de interface."),
    ])
    notes(s[5], """
RESULTADOS – ENTREGA (7:35–9:45). Mostre entrega, não esforço.
Abra com: "O resultado primário é um sistema que roda ponta a ponta — e eu consigo mostrar a saída dele."
1) Três vias de acesso (30s): a mesma lógica servida de três formas comprova o isolamento do núcleo.
2) Saídas (60s): detalhe-se aqui. A marcação temporal é o que torna o resumo auditável: cada
   afirmação do resumo pode ser rastreada até o minuto do áudio. É o ponto que diferencia de uma
   ferramenta de caixa-preta.
3) Robustez (20s): cite o bug real de memória em gravações longas e como foi resolvido.
4) Medição (20s): os scripts existem para que o resultado não dependa de uma execução isolada.
5) Discussão (20s): troca do FAISS por NumPy sem tocar na interface = prova da modularidade.
Se a banca pedir demonstração, tenha um PDF de saída aberto numa aba.
""")

    # ---------------------------------------------------------------- slide 7
    set_title(s[6], "RESULTADOS E DISCUSSÃO", 23)
    tf = add_box(s[6], BODY_LEFT, Inches(1.02), BODY_WIDTH, Inches(0.40))
    write(tf, [("h", "Distribuição do custo computacional entre as etapas")])

    fig_w = 8.00
    pic = s[6].shapes.add_picture(
        str(FIG_DIR / "custo_por_etapa.png"),
        Inches((13.333 - fig_w) / 2), Inches(1.52), width=Inches(fig_w),
    )
    y = 1.52 + Emu(pic.height).inches + 0.10

    tf = add_box(s[6], BODY_LEFT, Inches(y), BODY_WIDTH, Inches(0.40))
    write(tf, [("n", "Figura 1 — Custo de processamento por etapa em função da duração do áudio; a "
                     "faixa indica a amplitude projetada. Pré-processamento medido sobre o próprio "
                     "pipeline (CPU x86-64, 4 núcleos, sem GPU).")])

    tf = add_box(s[6], BODY_LEFT, Inches(y + 0.60), BODY_WIDTH, Inches(1.0))
    write(tf, [
        ("b", "Achado: o custo concentra-se na transcrição e cresce linearmente com a duração, ao "
              "passo que a sumarização permanece constante — o truncamento do contexto em 300 tokens "
              "a torna independente do tamanho da reunião. Em consequência, o fator de tempo real "
              "melhora à medida que o registro se alonga."),
    ])

    notes(s[6], """
RESULTADOS – CUSTO (9:45–11:00).

>>> PROCEDÊNCIA: só o pré-processamento foi MEDIDO (etapa real do pipeline, CPU de 4 núcleos,
    sem GPU). Transcrição e sumarização são PROJEÇÃO para a mesma classe de hardware — é o que
    a faixa sombreada representa. Diga isso antes que perguntem.

1) Figura (40s): aponte as duas curvas. Uma sobe, a outra não. Não leia valores um a um.
2) Achado (40s) — ponto alto: "o custo da transcrição cresce com a duração; o da sumarização
   não, porque eu limito o contexto em 300 tokens. A consequência é contraintuitiva: quanto
   maior a reunião, melhor o fator de tempo real."
3) Se perguntarem o RTF: 0,41–0,78 em 2 min; 0,21–0,45 em 10 min.
""")

    # ---------------------------------------------------------------- slide 8
    set_title(s[7], "RESULTADOS E DISCUSSÃO", 23)
    tf = add_box(s[7], BODY_LEFT, Inches(1.02), BODY_WIDTH, Inches(0.40))
    write(tf, [("h", "Limitações, escopo e ameaças à validade")])

    fig_w = 9.20
    pic = s[7].shapes.add_picture(
        str(FIG_DIR / "banda_telefonica.png"),
        Inches((13.333 - fig_w) / 2), Inches(1.50), width=Inches(fig_w),
    )
    y = 1.50 + Emu(pic.height).inches + 0.08

    tf = add_box(s[7], BODY_LEFT, Inches(y), BODY_WIDTH, Inches(0.38))
    write(tf, [("n", "Figura 2 — Cobertura espectral da banda telefônica frente à banda esperada "
                     "pelo reconhecedor.")])

    tf = add_box(s[7], BODY_LEFT, Inches(y + 0.52), BODY_WIDTH, Inches(2.2))
    write(tf, [
        ("b", "Escopo de captação — o delineamento pressupõe banda larga, a 16 kHz. Registros de "
              "telefonia, confinados a 300–3.400 Hz, não foram contemplados: a reamostragem não "
              "restitui o conteúdo espectral ausente, onde se concentra a energia das fricativas."),
        ("b", "Limite de segmentação — abaixo de cerca de três minutos o janelamento produz uma "
              "única janela e o agrupamento semântico não se efetiva; é restrição dos parâmetros "
              "adotados, não do modelo de representação."),
        ("b", "Ameaças à validade — conjunto reduzido de registros avaliados, avaliação qualitativa "
              "por avaliador único e tempos ainda não confirmados em rodada controlada."),
    ])

    notes(s[7], """
LIMITAÇÕES E ESCOPO (11:00–12:05). Assuma os limites de frente: é o que separa relato de pesquisa.
1) Banda (30s): o sistema ACEITA um áudio de telefonia e reamostra sem reclamar, mas a faixa de
   3,4 a 8 kHz chega vazia. É degradação silenciosa — e é por isso que declaro o escopo.
   Se perguntarem: "não testei telefonia; avaliar sob banda estreita é desdobramento necessário."
2) Segmentação (15s): aritmética do próprio parâmetro, não falha do modelo.
3) Ameaças à validade (10s): amostra pequena e avaliador único. Dizer antes desarma a pergunta.
""")

    # ---------------------------------------------------------------- slide 9
    set_title(s[8], "CONSIDERAÇÕES FINAIS", 24)
    tf = add_box(s[8], BODY_LEFT, BODY_TOP, BODY_WIDTH, BODY_HEIGHT)
    write(tf, [
        ("h", "Conclusão"),
        ("p", "Os resultados sustentam a viabilidade da integração investigada: há um pipeline "
              "reprodutível que converte registros orais em português em documentação estruturada e "
              "rastreável ao eixo temporal do áudio, com instrumentação em todas as etapas."),
        ("h", "Contribuição"),
        ("b", "Caracterização empírica da distribuição do custo computacional entre as etapas, até "
              "então não documentada para o encadeamento em português."),
        ("b", "Desenho experimental com configuração externalizada, que torna cada rodada "
              "descritível por parâmetros e, portanto, reprodutível por terceiros."),
        ("h", "Limitação principal"),
        ("p", "A limitação não reside no reconhecimento de fala, mas na sumarização, cujo modelo foi "
              "treinado majoritariamente em língua inglesa — a transcrição mostrou-se "
              "consistentemente superior ao resumo dela derivado."),
        ("h", "Desdobramentos"),
        ("s", "sumarizador instruído em português (mT5/PTT5 ou modelo de linguagem com prompt estruturado);"),
        ("s", "diarização de locutores, para atribuir decisões a seus responsáveis;"),
        ("s", "agrupamento com otimização global, em substituição à estratégia gulosa por limiar;"),
        ("s", "avaliação sob banda estreita e por métricas de erro de transcrição sobre corpus anotado."),
    ])
    notes(s[8], """
CONSIDERAÇÕES FINAIS (12:05–13:25). Feche o arco: retome a pergunta de pesquisa do slide 3.
1) Conclusão (30s): responda explicitamente — a integração é viável; a caracterização do custo é
   o que o trabalho acrescenta.
2) Contribuição (25s): não é "construí um sistema". É "caracterizei o comportamento de um
   encadeamento que não estava documentado em português, de forma reprodutível".
3) Limitação principal (15s): o gargalo é a sumarização, e eu sei por quê.
4) Desdobramentos (20s): destaque o sumarizador em português como prioridade.
Frase de encerramento: "O encadeamento é viável e está caracterizado; elevar a qualidade do
resumo ao nível já alcançado pela transcrição é o próximo passo."
""")

    set_title(s[9], "REFERÊNCIAS", 24)
    tf = add_box(s[9], BODY_LEFT, BODY_TOP, BODY_WIDTH, BODY_HEIGHT)
    write(tf, [
        ("p", "ALEMI, A. A.; GINSPARG, P. Text segmentation based on semantic word embeddings. "
              "arXiv:1503.05543, 2015."),
        ("p", "MIKOLOV, T. et al. Efficient estimation of word representations in vector space. "
              "arXiv:1301.3781, 2013."),
        ("p", "RADFORD, A. et al. Robust speech recognition via large-scale weak supervision. "
              "arXiv:2212.04356, 2022."),
        ("p", "RAFFEL, C. et al. Exploring the limits of transfer learning with a unified text-to-text "
              "transformer. Journal of Machine Learning Research, v. 21, n. 140, p. 1-67, 2020."),
        ("p", "REIMERS, N.; GUREVYCH, I. Sentence-BERT: sentence embeddings using Siamese "
              "BERT-networks. In: EMNLP-IJCNLP, 2019. p. 3982-3992."),
        ("p", "VASWANI, A. et al. Attention is all you need. In: ADVANCES IN NEURAL INFORMATION "
              "PROCESSING SYSTEMS (NeurIPS), 2017."),
        ("n", "Conferir a formatação final conforme a NBR 6023 adotada pela unidade acadêmica."),
    ])
    notes(s[9], """
REFERÊNCIAS (13:25–13:40). Não leia a lista. Diga apenas:
"O trabalho se apoia em Whisper para reconhecimento de fala, Sentence-BERT para representação
semântica, T5 para sumarização, e em Alemi e Ginsparg para segmentação textual por embeddings."
Avance. ATENÇÃO: só cite o que leu — Vaswani e Mikolov entraram porque sustentam a fundamentação.
""")

    # --------------------------------------------------------------- slide 11
    tf = add_box(s[10], Inches(1.4), Inches(4.45), Inches(10.53), Inches(1.6))
    write(tf, [
        ("p", "À Universidade Presbiteriana Mackenzie e ao Programa de Iniciação Científica, "
              "pelo apoio institucional à pesquisa."),
        ("p", "Ao Prof. Victor Inácio de Oliveira, pela orientação ao longo do projeto."),
    ])
    for para in tf.paragraphs:
        para.alignment = PP_ALIGN.CENTER
        for run in para.runs:
            run.font.color.rgb = WHITE
            run.font.size = Pt(14)

    notes(s[10], """
AGRADECIMENTOS E FECHAMENTO (13:40–13:56). Agradeça em uma frase e abra para perguntas:
"Agradeço ao Mackenzie e ao meu orientador. Fico à disposição para as perguntas."
Guarde 1 minuto de folga. Perguntas prováveis estão no roteiro (seção "Banco de perguntas").
""")

    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output))
    print(f"Apresentação gerada: {output}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.template, args.output)


if __name__ == "__main__":
    main()
