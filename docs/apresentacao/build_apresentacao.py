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
from pptx.util import Inches, Pt

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


def add_table(slide, left, top, width, headers, rows, col_widths=None):
    """Insere uma tabela formatada com a identidade visual do template."""
    n_rows, n_cols = len(rows) + 1, len(headers)
    height = Inches(0.32) * n_rows
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
            run.font.name, run.font.size = FONT, Pt(11)
            run.font.bold = True
            run.font.color.rgb = WHITE

    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(value)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if i % 2 else RGBColor(0xF2, 0xF4, 0xF6)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.05)
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            for run in para.runs:
                run.font.name, run.font.size = FONT, Pt(11)
                run.font.color.rgb = INK
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
    reorder(prs, [0, 1, 2, 3, 8, 4, 9, 5, 6, 7])

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
        ("p", "Reuniões concentram decisões, pendências e encaminhamentos, mas o registro depende de "
              "anotação manual: é custoso, parcial e raramente rastreável ao que foi efetivamente dito."),
        ("h", "Contexto tecnológico"),
        ("b", "Reconhecimento automático de fala (ASR) atingiu robustez multilíngue com modelos tipo Whisper."),
        ("b", "Embeddings de sentença (Sentence-BERT) permitem medir proximidade semântica entre trechos."),
        ("b", "Modelos seq2seq (T5) permitem condensar texto sob instrução em linguagem natural."),
        ("h", "Lacuna identificada"),
        ("p", "As soluções comerciais equivalentes são proprietárias, orientadas ao inglês e dependentes de "
              "nuvem — o que impede auditoria do processo e levanta restrições de privacidade sobre o áudio."),
        ("h", "Objetivo geral"),
        ("p", "Desenvolver um sistema modular, reprodutível e executável localmente que converta áudio de "
              "reunião em português em documentação acionável: decisões, pendências e próximos passos."),
        ("h", "Objetivos específicos"),
        ("s", "Integrar ASR, estruturação semântica e sumarização num pipeline único e instrumentado."),
        ("s", "Isolar o núcleo de IA das camadas de uso, tornando-o reutilizável e testável."),
        ("s", "Definir um protocolo de avaliação reprodutível para medir desempenho e qualidade."),
    ])
    notes(s[2], """
INTRODUÇÃO (0:45–3:15). Não leia os bullets.
1) Problema (40s): a ata manual é o gargalo; o que se perde não é o áudio, é a decisão.
2) Contexto (40s): três famílias de modelos maduras — ASR, embeddings de sentença, seq2seq —
   que até então eram usadas isoladamente.
3) Lacuna (30s): o diferencial não é "transcrever", é fazê-lo de forma auditável, em português
   e sem enviar o áudio para terceiros.
4) Objetivo (30s): leia o objetivo geral devagar — é a frase que a banca vai cobrar no final.
Transição: "Para chegar a isso, estruturei o trabalho como engenharia de pipeline."
""")

    # ---------------------------------------------------------------- slide 4
    set_title(s[3], "METODOLOGIA", 24)
    tf = add_box(s[3], BODY_LEFT, BODY_TOP, BODY_WIDTH, Inches(0.42))
    write(tf, [("h", "Arquitetura do pipeline — cinco estágios encadeados")])
    tf = add_box(s[3], BODY_LEFT, CONTENT_TOP, BODY_WIDTH, Inches(4.75))
    write(tf, [
        ("p", "Abordagem de pesquisa aplicada e experimental: o problema é decomposto em etapas com "
              "responsabilidade única e saída bem definida para a etapa seguinte."),
        ("b", "1.  Pré-processamento do áudio (librosa) — remoção de silêncio nas extremidades (top_db = 25), "
              "normalização de pico, subtração espectral em blocos de 60 s e reamostragem para 16 kHz mono."),
        ("b", "2.  Transcrição / ASR (faster-whisper) — decodificação por feixe (beam_size = 5), filtro de "
              "atividade de voz (VAD) e idioma fixado em pt; saída segmentada com marcação temporal."),
        ("b", "3.  Estruturação semântica (Sentence-BERT) — tokenização e reorganização em janelas "
              "deslizantes de 500 tokens com sobreposição de 50; cada janela vira um vetor normalizado em L2."),
        ("b", "4.  Agrupamento temático — similaridade de cosseno contra limiar de 0,78, com fusão incremental "
              "gulosa e atualização do centroide; cada bloco é remapeado ao eixo temporal da reunião."),
        ("b", "5.  Sumarização (T5) — instruções em linguagem natural por seção (decisões / pendências / "
              "próximos passos), com corte controlado de contexto, somadas a uma visão geral da transcrição."),
        ("n", "Exportação: transcrição em TXT e PDF; resumo estruturado em PDF e JSON."),
    ])
    add_pipeline_diagram(s[3], Inches(0.62), Inches(5.62), [
        ("Áudio da\nreunião", False),
        ("Pré-\nprocessamento", False),
        ("Transcrição\nWhisper (ASR)", True),
        ("Embeddings\nSentence-BERT", True),
        ("Agrupamento\npor cosseno", True),
        ("Resumo T5\n+ exportação", False),
    ])
    notes(s[3], """
METODOLOGIA – PIPELINE (3:15–6:15). Este é o slide central: ande pelas cinco caixas.
Ancoragem: "A ideia é ir do sinal sonoro ao texto, do texto a tópicos, e de tópicos à decisão."
1) Pré-processamento (30s): justifique — lixo entra, lixo sai. A subtração espectral em blocos de
   60 s foi necessária porque gravações longas estouravam a memória.
2) ASR (40s): beam search custa mais tempo, mas reduz erro; VAD evita alucinação em silêncio;
   fixar pt evita troca espúria de idioma.
3) Embeddings (35s): explique a janela deslizante — a sobreposição evita cortar uma ideia ao meio.
4) Agrupamento (35s): cosseno com limiar 0,78; é guloso, decisão consciente (volta nas limitações).
5) Sumarização (30s): o resumo não é livre, é guiado por três perguntas fixas.
Se o tempo apertar, resuma 1 e 5 e preserve 3 e 4 — é onde está a contribuição técnica.
""")

    # ---------------------------------------------------------------- slide 5
    set_title(s[4], "METODOLOGIA", 24)
    tf = add_box(s[4], BODY_LEFT, BODY_TOP, BODY_WIDTH, Inches(0.42))
    write(tf, [("h", "Decisões de projeto, reprodutibilidade e verificação")])
    tf = add_box(s[4], BODY_LEFT, CONTENT_TOP, BODY_WIDTH, Inches(4.75))
    write(tf, [
        ("b", "Arquitetura em camadas — o núcleo de IA (src/) é independente das camadas de uso "
              "(backend/): linha de comando, API FastAPI, painel Streamlit e front-end Next.js."),
        ("s", "Consequência metodológica: o núcleo pode ser testado e reutilizado sem subir interface."),
        ("b", "Configuração externalizada — modelo de ASR, modelo de embeddings, sumarizador, tamanho de "
              "janela, sobreposição, limiar de similaridade e limites de upload são variáveis de ambiente."),
        ("s", "Consequência metodológica: um experimento é descrito por um conjunto de variáveis, "
              "não por uma alteração de código — o que torna a rodada reprodutível."),
        ("b", "Instrumentação — toda execução devolve stage_timings: tempo de pré-processamento, "
              "transcrição, análise semântica, sumarização, exportação e tempo total de parede."),
        ("b", "Verificação — suíte automatizada em pytest com dublês de modelos: 15 testes em 6 módulos "
              "cobrindo transcrição, embeddings, sumarização, validação de upload, API e integração."),
        ("b", "Protocolo experimental — 2 a 4 cenários de áudio com perfis distintos: curto e limpo; "
              "médio com múltiplos falantes; com ruído de fundo; com silêncio inicial prolongado."),
        ("s", "Para cada cenário registram-se configuração, métricas automáticas e checklist qualitativo."),
    ])
    notes(s[4], """
METODOLOGIA – RIGOR (6:15–8:00). Aqui você mostra método, não código.
Mensagem única: "As decisões de arquitetura foram tomadas para que o experimento fosse reprodutível."
1) Camadas (25s): o núcleo não sabe que existe uma interface.
2) Configuração externalizada (30s): este é o argumento mais forte de rigor — uma rodada é descrita
   por variáveis de ambiente, então outro pesquisador reproduz sem tocar no código.
3) Instrumentação (25s): sem medir por etapa não se sabe onde está o custo.
4) Testes (20s): dublês de modelos permitem testar a lógica sem baixar modelos pesados.
5) Protocolo (20s): os quatro perfis de áudio não são arbitrários — cada um estressa uma etapa.
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
RESULTADOS – PARTE 1 (8:00–10:30). Mostre entrega, não esforço.
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
    tf = add_box(s[6], BODY_LEFT, BODY_TOP, BODY_WIDTH, Inches(0.42))
    write(tf, [("h", "Avaliação experimental, limitações e ameaças à validade")])

    tf = add_box(s[6], BODY_LEFT, CONTENT_TOP, BODY_WIDTH, Inches(0.95))
    write(tf, [
        ("b", "Métricas instrumentadas por execução: duração do áudio, tempo de cada etapa, tempo total, "
              "fator de tempo real (RTF = tempo total ÷ duração do áudio), número de segmentos, número de "
              "blocos semânticos e extensão da transcrição; WER/CER quando há transcrição de referência."),
    ])

    add_table(
        s[6],
        BODY_LEFT, Inches(2.52), Inches(10.0),
        ["Cenário de áudio", "Duração (s)", "Tempo total (s)", "RTF", "Segmentos", "Blocos"],
        [
            ["A1 — curto, um locutor, ambiente calmo", "—", "—", "—", "—", "—"],
            ["A2 — médio, múltiplos falantes", "—", "—", "—", "—", "—"],
            ["A3 — com ruído de fundo / microfone distante", "—", "—", "—", "—", "—"],
        ],
        col_widths=[Inches(4.0), Inches(1.25), Inches(1.45), Inches(0.9), Inches(1.25), Inches(1.15)],
    )

    tf = add_box(s[6], BODY_LEFT, Inches(3.84), BODY_WIDTH, Inches(0.34))
    write(tf, [("n", "Tabela 1 — Rodada de referência (scripts/benchmark_pipeline.py; "
                     "configuração conforme docs/evaluation_protocol.md).")])

    tf = add_box(s[6], BODY_LEFT, Inches(4.26), BODY_WIDTH, Inches(2.1))
    write(tf, [
        ("h", "Limitações e ameaças à validade"),
        ("s", "Idioma fixado em português: o sistema não trata reuniões multilíngues."),
        ("s", "Agrupamento guloso por limiar — a ordem de chegada influencia os blocos, pois não há "
              "otimização global como em agrupamento hierárquico ou espectral."),
        ("s", "O sumarizador (T5 pequeno, treinado majoritariamente em inglês) é o gargalo de qualidade: "
              "a transcrição é consistentemente melhor que o resumo."),
        ("s", "Ausência de diarização (o sistema registra o que foi dito, não quem disse) e avaliação "
              "qualitativa conduzida por um único avaliador sobre um conjunto reduzido de áudios."),
    ])

    notes(s[6], """
RESULTADOS – PARTE 2 (10:30–12:00).
>>> ANTES DE APRESENTAR: preencher a Tabela 1 com os números da sua rodada.
    Comando: python scripts/benchmark_pipeline.py --audio a1.wav a2.wav a3.wav \
             --output docs/runs/rodada_final.md
    Se não houver rodada, troque a tabela por uma frase honesta: "a infraestrutura de medição está
    entregue; a rodada controlada sobre o conjunto de áudios é o passo imediato."
1) Métricas (30s): explique RTF — abaixo de 1 significa processar mais rápido que o tempo do áudio.
2) Tabela (30s): comente a tendência, não os números um a um. Diga onde está o custo dominante.
3) Limitações (45s): assuma-as de frente; a banca valoriza quem conhece o próprio limite.
   Frase forte: "a transcrição é consistentemente melhor que o resumo, e eu sei por quê — o
   sumarizador é um modelo pequeno treinado majoritariamente em inglês."
4) Ameaças à validade (15s): amostra pequena e avaliador único — antecipe a pergunta da banca.
""")

    # ---------------------------------------------------------------- slide 8
    set_title(s[7], "CONSIDERAÇÕES FINAIS", 24)
    tf = add_box(s[7], BODY_LEFT, BODY_TOP, BODY_WIDTH, BODY_HEIGHT)
    write(tf, [
        ("h", "Conclusão"),
        ("p", "O objetivo foi atingido no nível de sistema: existe um pipeline reprodutível que converte "
              "áudio de reunião em português em documentação estruturada e rastreável ao tempo do áudio, "
              "com instrumentação de desempenho em todas as etapas."),
        ("h", "Contribuição"),
        ("b", "Uma arquitetura de referência aberta e modular que integra ASR, estruturação semântica e "
              "sumarização, executável localmente — sem enviar o áudio da reunião a terceiros."),
        ("b", "Um protocolo de avaliação e ferramentas de medição que permitem comparar configurações de "
              "forma reprodutível, e não apenas relatar uma execução isolada."),
        ("h", "Aprendizados"),
        ("b", "A separação entre núcleo de IA e camadas de uso foi decisiva para evoluir o sistema sem retrabalho."),
        ("b", "Medir por etapa, e não apenas o tempo total, foi o que revelou onde o custo realmente está."),
        ("h", "Trabalhos futuros"),
        ("s", "sumarizador instruído em português (mT5/PTT5 ou modelo de linguagem com prompt estruturado);"),
        ("s", "diarização de falantes, para atribuir decisões a seus responsáveis;"),
        ("s", "agrupamento com otimização global, substituindo a estratégia gulosa por limiar;"),
        ("s", "avaliação com WER/CER sobre corpus anotado e julgamento humano do resumo por múltiplos avaliadores."),
    ])
    notes(s[7], """
CONSIDERAÇÕES FINAIS (12:00–13:30). Feche o arco: retome o objetivo do slide 3.
1) Conclusão (30s): responda explicitamente "o objetivo foi atingido?" — e qualifique: no nível de
   sistema sim; no nível de qualidade do resumo, parcialmente.
2) Contribuição (25s): auditabilidade e privacidade são os dois diferenciais. Diga isso em voz alta.
3) Aprendizados (20s): mostra maturidade de engenharia.
4) Trabalhos futuros (25s): não liste os quatro com o mesmo peso — destaque o sumarizador em
   português como a próxima prioridade, porque é o gargalo que você identificou nos resultados.
Frase de encerramento: "Em resumo: o sistema já transforma reunião falada em documentação
rastreável; o próximo passo é elevar a qualidade do resumo ao nível já alcançado pela transcrição."
""")

    # ---------------------------------------------------------------- slide 9
    set_title(s[8], "REFERÊNCIAS", 24)
    tf = add_box(s[8], BODY_LEFT, BODY_TOP, BODY_WIDTH, BODY_HEIGHT)
    write(tf, [
        ("p", "ALEMI, A. A.; GINSPARG, P. Text segmentation based on semantic word embeddings. "
              "arXiv:1503.05543, 2015."),
        ("p", "McFEE, B. et al. librosa: audio and music signal analysis in Python. In: PROCEEDINGS OF THE "
              "14th PYTHON IN SCIENCE CONFERENCE (SciPy), 2015. p. 18-25."),
        ("p", "RADFORD, A. et al. Robust speech recognition via large-scale weak supervision. "
              "arXiv:2212.04356, 2022."),
        ("p", "RAFFEL, C. et al. Exploring the limits of transfer learning with a unified text-to-text "
              "transformer. Journal of Machine Learning Research, v. 21, n. 140, p. 1-67, 2020."),
        ("p", "REIMERS, N.; GUREVYCH, I. Sentence-BERT: sentence embeddings using Siamese BERT-networks. "
              "In: PROCEEDINGS OF THE 2019 CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING "
              "(EMNLP-IJCNLP), 2019. p. 3982-3992."),
        ("n", "Conferir a formatação final conforme a NBR 6023 adotada pela unidade acadêmica."),
    ])
    notes(s[8], """
REFERÊNCIAS (13:30–13:45). Não leia a lista. Diga apenas:
"O trabalho se apoia em quatro referências centrais: Whisper para reconhecimento de fala,
Sentence-BERT para representação semântica, T5 para sumarização e Alemi e Ginsparg para
segmentação textual por embeddings." Avance.
""")

    # --------------------------------------------------------------- slide 10
    tf = add_box(s[9], Inches(1.4), Inches(4.45), Inches(10.53), Inches(1.6))
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

    notes(s[9], """
AGRADECIMENTOS E FECHAMENTO (13:45–14:00). Agradeça em uma frase e abra para perguntas:
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
