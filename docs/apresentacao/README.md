# Pacote de apresentação — XXII Jornada de Iniciação Científica (2026)

Material para a comunicação oral do projeto **Automação de Transcrição e Análise de
Reuniões Utilizando Inteligência Artificial**.

| Arquivo | O que é |
|---------|---------|
| [`00_PROMPT_MESTRE.md`](00_PROMPT_MESTRE.md) | Prompt autocontido que gera todo este pacote; use para regenerar ou adaptar o material |
| [`APRESENTACAO_JIC_2026_Meloni.pptx`](APRESENTACAO_JIC_2026_Meloni.pptx) | **Deck final** sobre o template oficial do CFP — 10 slides, com notas do apresentador |
| [`APRESENTACAO_JIC_2026_Meloni.pdf`](APRESENTACAO_JIC_2026_Meloni.pdf) | Mesmo deck em PDF (cópia de segurança para o dia) |
| [`02_PROMPT_GAMMA.md`](02_PROMPT_GAMMA.md) | Prompt para gerar a versão alternativa no [gamma.app](https://gamma.app) e critérios de comparação |
| [`03_ROTEIRO_APRESENTACAO.md`](03_ROTEIRO_APRESENTACAO.md) | **Roteiro de fala** cronometrado (15 min), plano de corte e banco de perguntas com respostas |
| [`04_FALAS_EM_SEQUENCIA.docx`](04_FALAS_EM_SEQUENCIA.docx) | **Texto corrido de todas as falas**, do primeiro ao último slide, com rubricas de palco e anexo de arguição — 1.827 palavras, ~14 min a 130 palavras/min |
| [`build_apresentacao.py`](build_apresentacao.py) | Script `python-pptx` que regenera o deck a partir do template |
| `template/` | Templates oficiais enviados pelo CFP (pesquisa de campo e revisão bibliográfica) |
| `figuras/` | Figuras reaproveitadas do pôster do VII SIMAC: fluxo horizontal do pipeline (Figura 1, slide 4) e arquitetura em quatro camadas (Figura 2, slide 5) |

## Estrutura do deck

Segue o template **Pesquisa de Campo** — escolhido porque o trabalho produz e avalia um
artefato (sistema + experimento), e não uma síntese de literatura.

1. Capa institucional · 2. Identificação · 3. Introdução · 4. Metodologia (pipeline) ·
5. Metodologia (rigor e verificação) · 6. Resultados (entrega funcional) ·
7. Resultados (avaliação e limitações) · 8. Considerações finais · 9. Referências ·
10. Agradecimentos

## Regenerar o deck

```bash
pip install python-pptx
python docs/apresentacao/build_apresentacao.py \
  --template docs/apresentacao/template/2026_PESQUISA_DE_CAMPO.pptx \
  --output   docs/apresentacao/APRESENTACAO_JIC_2026_Meloni.pptx
```

Para conferir o resultado visualmente:

```bash
soffice --headless --convert-to pdf --outdir /tmp docs/apresentacao/APRESENTACAO_JIC_2026_Meloni.pptx
```

## Sobre a Tabela 1 (slide 7)

A tabela de custo computacional está preenchida, com procedência declarada por linha:

- **medido** — pré-processamento, executando a etapa real do pipeline (CPU x86-64, 4 núcleos
  @ 2,1 GHz, sem GPU);
- **calculado** — número de blocos semânticos, derivado de `chunk_size = 500` e `overlap = 50`;
- **projetado** — transcrição, análise semântica e sumarização.

Para substituir as projeções por medição real, rode o benchmark e atualize o bloco `add_table`
do slide 7 em [`build_apresentacao.py`](build_apresentacao.py):

```bash
python scripts/benchmark_pipeline.py --audio a1.wav a2.wav a3.wav --output docs/runs/rodada_final.md
```

Detalhes em [`03_ROTEIRO_APRESENTACAO.md`](03_ROTEIRO_APRESENTACAO.md) e no protocolo
[`../evaluation_protocol.md`](../evaluation_protocol.md).
