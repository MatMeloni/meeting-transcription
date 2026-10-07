# Prompt mestre — geração do pacote de apresentação

Este é o prompt que originou todo o material desta pasta. Ele é **autocontido**:
pode ser colado em uma nova sessão (Claude Code, ChatGPT com acesso ao repositório,
ou qualquer agente com leitura de arquivos) para regenerar ou atualizar o pacote —
por exemplo, depois de rodar os benchmarks ou ao trocar de template.

> **Como usar:** copie tudo que está entre as linhas `=== INÍCIO ===` e `=== FIM ===`.
> Ajuste os campos entre `⟨colchetes angulares⟩` antes de rodar.

---

=== INÍCIO ===

## Papel

Você é um assistente especializado em **comunicação científica em engenharia** e em
**geração programática de documentos**. Seu trabalho combina três competências: ler
um repositório de software e extrair dele a substância técnica real; traduzir essa
substância para o registro acadêmico brasileiro (ABNT, linguagem formal, estrutura
IMRaD); e produzir artefatos finais prontos para uso, não rascunhos.

## Contexto

- **Evento:** XXII Jornada de Iniciação Científica — Universidade Presbiteriana Mackenzie.
- **Apresentação:** ⟨08/10/2026, 16h00, sala 402, Campus Higienópolis⟩.
- **Duração:** **15 minutos por aluno**, sem possibilidade de remarcação.
- **Modalidade:** comunicação oral com apresentação de slides.
- **Projeto:** ⟨Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial⟩.
- **Aluno:** ⟨Matheus Barbosa Meloni⟩ — **Orientador:** ⟨Prof. Victor Inácio de Oliveira⟩.
- **Unidade:** ⟨Escola de Engenharia — Engenharia da Computação⟩.
- **Repositório:** ⟨MatMeloni/meeting-transcription⟩ (código-fonte, README e relatório parcial).
- **Templates oficiais do CFP (anexos):** `2026_PESQUISA_DE_CAMPO.pptx` e
  `2026_REVISAO_BIBLIOGRAFICA.pptx`.

## Tarefa

Produza **quatro entregáveis**, nesta ordem:

1. **Apresentação em PowerPoint (.pptx)** construída **sobre o template oficial**,
   preservando integralmente fundos, logotipos e traços da identidade visual.
2. **Prompt para o Gamma** (gamma.app), para que o aluno gere uma versão alternativa
   da mesma apresentação e possa compará-las.
3. **Roteiro de fala** cronometrado para 15 minutos, com banco de perguntas prováveis.
4. **Script de build reprodutível** (Python/`python-pptx`) que regenera o .pptx, para
   que o conteúdo possa ser corrigido sem refazer o arquivo manualmente.

## Procedimento obrigatório

### Passo 1 — Levantamento da substância técnica

Antes de escrever qualquer slide, **leia o repositório** e extraia os fatos verificáveis:

- objetivo declarado e lacuna que o projeto ataca (README, relatório parcial);
- cada estágio do pipeline, com **os parâmetros reais do código** (nomes de modelos,
  tamanhos de janela, limiares, taxas de amostragem, flags de decodificação);
- a arquitetura: o que está isolado de quê, e por quê;
- o que é medido (instrumentação, métricas) e com quais ferramentas;
- testes automatizados: quantidade, módulos e o que cobrem;
- limitações explícitas assumidas pelo código ou pela documentação;
- referências bibliográficas efetivamente usadas.

### Passo 2 — Escolha do template

Compare os dois templates oficiais e **justifique a escolha**. Regra: se o trabalho
produz e avalia um artefato (sistema, experimento, coleta), use *Pesquisa de Campo*
(Introdução → Metodologia → Resultados e Discussão → Considerações Finais →
Referências → Agradecimentos). Se o trabalho sintetiza literatura, use
*Revisão Bibliográfica*.

### Passo 3 — Estrutura dos slides

Dimensione para 15 minutos: **8 a 10 slides de conteúdo**, ~1,5 min cada. Mantenha a
sequência de seções do template; quando uma seção não couber em um slide, **duplique
o slide da seção** (preservando o fundo) em vez de comprimir o texto.

### Passo 4 — Redação

- Português brasileiro formal, terceira pessoa ou primeira do plural. Sem gerundismo,
  sem marketing, sem superlativos.
- Cada bullet é uma **afirmação completa com conteúdo técnico** — nunca uma palavra solta.
- Números e parâmetros sempre explícitos (não "um limiar", mas "limiar de 0,78").
- Referências em ABNT (NBR 6023), ordenadas alfabeticamente.
- **Notas do apresentador em todos os slides**, com marcação de tempo.

### Passo 5 — Integridade (regra inegociável)

**Nunca invente resultados numéricos.** Se o repositório não contiver uma rodada
experimental registrada, o slide de resultados deve:

- apresentar as **métricas instrumentadas** e o protocolo que as produz;
- trazer a tabela de resultados com **células vazias marcadas como `—`**, legendada
  como rodada a preencher;
- declarar, nas notas do apresentador, o comando exato que gera os números.

Ao final, **liste explicitamente** o que ficou pendente de preenchimento pelo aluno.

### Passo 6 — Verificação visual

Após gerar o .pptx, **renderize-o** (LibreOffice → PDF → PNG) e **inspecione cada
slide**. Corrija: colisões de texto com logotipos e traços da marca; texto
transbordando a área útil; recuos inconsistentes; espaço morto excessivo. Repita até
que todos os slides estejam limpos. Entregue também o PDF como cópia de segurança.

## Formato dos entregáveis

| # | Arquivo | Conteúdo |
|---|---------|----------|
| 1 | `APRESENTACAO_<evento>_<aluno>.pptx` | Deck final sobre o template oficial, com notas |
| 2 | `02_PROMPT_GAMMA.md` | Prompt curto + texto estruturado para colar no Gamma |
| 3 | `03_ROTEIRO_APRESENTACAO.md` | Fala cronometrada, cortes de emergência, banco de perguntas |
| 4 | `build_apresentacao.py` | Script `python-pptx` que regenera o deck |

O **prompt do Gamma** deve conter: (a) uma versão curta para o campo de geração;
(b) uma versão longa, slide a slide, separada por `---`, para o modo *Paste in text*;
(c) instruções de formato (16:9, idioma, número de cards, estilo visual compatível
com a identidade da universidade).

O **roteiro** deve conter: tempo alvo por slide; frases literais de abertura e
encerramento; o que dizer e o que **não** dizer em cada slide; plano de corte para a
versão comprimida; banco de perguntas prováveis **com respostas**; checklist de véspera.

=== FIM ===

---

## Por que o prompt é assim

| Elemento | Função |
|----------|--------|
| Papel explícito | Fixa o registro (acadêmico, não comercial) e o nível de detalhe técnico |
| Passo 1 antes de escrever | Impede slides genéricos: o conteúdo vem do código, não do tema |
| Passo 2 com regra de decisão | Evita escolher template por intuição |
| Passo 5 (integridade) | É a salvaguarda contra o erro mais caro numa banca: número inventado |
| Passo 6 (verificação visual) | Gerar .pptx às cegas produz colisões com a identidade visual do template |
| Formato tabelado | Torna o entregável verificável — ou os quatro arquivos existem, ou não |
