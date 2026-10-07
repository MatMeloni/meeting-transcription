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
| [`build_apresentacao.py`](build_apresentacao.py) | Script `python-pptx` que regenera o deck a partir do template |
| `template/` | Templates oficiais enviados pelo CFP (pesquisa de campo e revisão bibliográfica) |

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

## ⚠️ Pendência

A **Tabela 1** (slide 7) está com células `—`. Preencha com uma rodada real antes de
apresentar — ver instruções em [`03_ROTEIRO_APRESENTACAO.md`](03_ROTEIRO_APRESENTACAO.md)
e o protocolo em [`../evaluation_protocol.md`](../evaluation_protocol.md).
