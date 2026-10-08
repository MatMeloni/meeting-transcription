const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, PageBreak,
  AlignmentType, BorderStyle, HeadingLevel, convertInchesToTwip,
} = require("docx");

const FONT = "Calibri";
const ACCENT = "C2185B";
const INK = "1A1A1A";
const SOFT = "5F6B76";

/** Converte **negrito** em runs. */
function rt(text, opts = {}) {
  return text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((piece) => {
    const bold = piece.startsWith("**") && piece.endsWith("**");
    return new TextRun({
      text: bold ? piece.slice(2, -2) : piece,
      bold: bold || opts.bold === true,
      italics: opts.italics,
      color: opts.color || INK,
      font: FONT,
      size: opts.size || 26,          // meio-pontos: 26 = 13 pt
    });
  });
}

/** Parágrafo de fala: 13 pt, entrelinha 1,5. */
const fala = (text) => new Paragraph({
  children: rt(text),
  spacing: { line: 360, after: 180 },
  alignment: AlignmentType.JUSTIFIED,
});

/** Rubrica de palco, em itálico. */
const rubrica = (text) => new Paragraph({
  children: rt(text, { italics: true, color: SOFT, size: 22 }),
  spacing: { line: 276, after: 160 },
  indent: { left: convertInchesToTwip(0.25) },
});

/** Cabeçalho de slide. */
const slide = (titulo, tempo) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 420, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 8, space: 6, color: ACCENT } },
  children: [
    new TextRun({ text: titulo, bold: true, color: ACCENT, font: FONT, size: 26 }),
    new TextRun({ text: ` ${tempo}`, bold: false, color: SOFT, font: FONT, size: 22 }),
  ],
});

const pergunta = (q) => new Paragraph({
  children: rt(q, { bold: true, color: ACCENT, size: 24 }),
  spacing: { before: 260, after: 100 },
});
const resposta = (a) => new Paragraph({
  children: rt(a, { size: 24 }),
  spacing: { line: 300, after: 120 },
  alignment: AlignmentType.JUSTIFIED,
  indent: { left: convertInchesToTwip(0.25) },
});

const corpo = [];

// ------------------------------------------------------------------ capa
corpo.push(new Paragraph({
  children: [new TextRun({ text: "Falas da apresentação — em sequência", bold: true, color: INK, font: FONT, size: 40 })],
  spacing: { after: 140 },
}));
corpo.push(new Paragraph({
  children: [new TextRun({ text: "Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial", color: SOFT, font: FONT, size: 26 })],
  spacing: { after: 60 },
}));
corpo.push(new Paragraph({
  children: [new TextRun({ text: "Matheus Barbosa Meloni  ·  orientação: Prof. Victor Inácio de Oliveira", color: SOFT, font: FONT, size: 24 })],
  spacing: { after: 60 },
}));
corpo.push(new Paragraph({
  children: [new TextRun({ text: "XXII Jornada de Iniciação Científica — Universidade Presbiteriana Mackenzie  ·  08/10, 16h00, sala 402, Campus Higienópolis", color: SOFT, font: FONT, size: 24 })],
  spacing: { after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, space: 10, color: ACCENT } },
}));
corpo.push(new Paragraph({
  children: rt("Texto corrido de tudo o que você fala, do primeiro ao último slide. O que está em *itálico e entre colchetes* é rubrica de palco — não se lê em voz alta. Tempo alvo: **14 minutos**, deixando um minuto de folga dentro dos quinze.", { italics: true, color: SOFT, size: 22 }),
  spacing: { before: 200, after: 200, line: 276 },
}));

// -------------------------------------------------------------- slides 1-2
corpo.push(slide("SLIDES 1–2 · ABERTURA", "0:00 – 0:45"));
corpo.push(rubrica("[Olhe para a banca, não para o telão. Fale devagar nesta primeira frase.]"));
corpo.push(fala("Boa tarde. Meu nome é Matheus Barbosa Meloni, sou aluno de Engenharia da Computação, e apresento o projeto Automação de Transcrição e Análise de Reuniões Utilizando Inteligência Artificial, desenvolvido sob orientação do professor Victor Inácio de Oliveira."));
corpo.push(fala("Vou começar com uma constatação simples: **toda reunião produz decisões, mas quase nenhuma produz um registro confiável dessas decisões.** É exatamente essa lacuna que este trabalho ataca."));
corpo.push(fala("Nos próximos minutos eu vou percorrer o problema, o método que adotei, o que o sistema efetivamente entrega, as limitações que identifiquei e os próximos passos."));

// ------------------------------------------------------------------ slide 3
corpo.push(slide("SLIDE 3 · INTRODUÇÃO", "0:45 – 3:15"));
corpo.push(fala("Começo pelo problema. O gargalo de uma reunião não é gravá-la — é transformar o que foi dito em algo acionável. Hoje isso depende de alguém anotando à mão, em paralelo à conversa. O resultado é um registro parcial, custoso de produzir e difícil de conferir. E o que se perde não é o áudio: é a decisão, o responsável e o prazo."));
corpo.push(fala("Do lado da tecnologia, três famílias de modelos amadureceram nos últimos anos. O reconhecimento automático de fala atingiu robustez multilíngue com modelos do tipo Whisper. Os modelos de representação de sentenças, como o Sentence-BERT, permitem medir proximidade semântica entre trechos de texto. E os modelos sequência-a-sequência, como o T5, permitem condensar texto sob instrução em linguagem natural. Essas três capacidades existiam de forma isolada. A pergunta que orientou o projeto foi: o que acontece quando eu as encadeio num pipeline único, com uma finalidade específica?"));
corpo.push(fala("Existem ferramentas comerciais que percorrem parte desse caminho. Mas são caixas fechadas, orientadas ao inglês e dependentes de nuvem. Para uma reunião com conteúdo sensível, enviar o áudio para um terceiro é um problema concreto — e, do ponto de vista científico, não é possível auditar um processo cujo funcionamento interno não se pode inspecionar. É aí que está a lacuna que este trabalho ocupa."));
corpo.push(rubrica("[Pausa. Esta é a frase que a banca vai cobrar no final — diga-a devagar, olhando para eles.]"));
corpo.push(fala("O objetivo geral, portanto, foi: **desenvolver um sistema modular, reprodutível e executável localmente, que converta áudio de reunião em português em documentação acionável — decisões, pendências e próximos passos.**"));
corpo.push(fala("Para chegar lá, defini três objetivos específicos: integrar reconhecimento de fala, estruturação semântica e sumarização num pipeline único e instrumentado; isolar o núcleo de inteligência artificial das camadas de uso, de modo que ele fosse reutilizável e testável; e definir um protocolo de avaliação reprodutível, que permitisse medir desempenho e qualidade."));
corpo.push(fala("Para chegar nisso, estruturei o trabalho como engenharia de pipeline."));

// ------------------------------------------------------------------ slide 4
corpo.push(slide("SLIDE 4 · METODOLOGIA — ARQUITETURA DO PIPELINE", "3:15 – 6:00"));
corpo.push(rubrica("[Slide central. Use o fluxo de setas na parte de baixo como trilho: aponte com a mão o estágio de que está falando.]"));
corpo.push(fala("A ideia metodológica central é ir do sinal sonoro ao texto, do texto a tópicos, e de tópicos à decisão. Cada etapa tem uma responsabilidade única e uma saída bem definida para a próxima. São cinco estágios, no fluxo da parte inferior do slide."));
corpo.push(fala("O primeiro é o **pré-processamento do áudio**. O princípio aqui é simples: lixo entra, lixo sai. Antes de qualquer modelo, eu corto o silêncio nas extremidades, normalizo a amplitude, atenuo o ruído por subtração espectral e reamostro para dezesseis quilohertz, mono. A subtração espectral é feita em blocos de sessenta segundos, porque gravações longas estouravam a memória quando processadas de uma vez só."));
corpo.push(fala("O segundo é a **transcrição**, com o Whisper, por meio da implementação faster-whisper. Uso busca em feixe de largura cinco, que custa mais tempo mas reduz o erro; o filtro de atividade de voz, que evita que o modelo gere texto em trechos de silêncio; e o idioma fixado em português. A saída preserva o tempo de início e de fim de cada segmento — e esse detalhe vai ser importante nos resultados."));
corpo.push(fala("O terceiro é a **estruturação semântica**. A transcrição vira uma sequência de tokens, reorganizada em janelas deslizantes de quinhentos tokens com sobreposição de cinquenta. A sobreposição evita que uma ideia seja cortada na fronteira entre duas janelas. Cada janela é convertida num vetor de embedding pelo Sentence-BERT, e normalizada."));
corpo.push(fala("O quarto é o **agrupamento temático**. Comparo cada janela com os blocos já formados por similaridade de cosseno: acima do limiar de zero vírgula setenta e oito, funde e atualiza o centroide; abaixo, abre um bloco novo. É uma estratégia incremental e gulosa, e eu volto a ela nas limitações. Cada bloco é remapeado para o eixo temporal da reunião."));
corpo.push(fala("O quinto é a **sumarização**, e aqui há uma escolha de desenho importante: o resumo não é livre. Sobre os blocos eu faço três perguntas fixas — que decisões foram tomadas, o que ficou pendente, quais os próximos passos — e o T5 responde a cada uma. Acrescento uma visão geral da transcrição completa. Ao final, o sistema exporta a transcrição em texto e PDF, e o resumo em PDF e JSON."));
corpo.push(rubrica("[Se estiver atrasado: resuma os estágios 1 e 5 em uma frase cada e preserve 3 e 4 — é onde está a contribuição técnica.]"));

// ------------------------------------------------------------------ slide 5
corpo.push(slide("SLIDE 5 · METODOLOGIA — DECISÕES DE PROJETO E VERIFICAÇÃO", "6:00 – 7:45"));
corpo.push(fala("Este slide trata das decisões de projeto, e a mensagem é uma só: **elas foram tomadas para que o experimento fosse reprodutível.**"));
corpo.push(fala("A primeira é a arquitetura em camadas. O núcleo de inteligência artificial é independente das camadas de uso — linha de comando, API, painel web. O núcleo não sabe que existe uma interface. Isso não é organização de pastas: é o que permite testá-lo e reutilizá-lo isoladamente."));
corpo.push(fala("A segunda é a configuração externalizada. Modelo de reconhecimento de fala, modelo de embeddings, sumarizador, tamanho de janela, sobreposição e limiar de similaridade são todos variáveis de ambiente. Isso significa que **uma rodada experimental passa a ser descrita por um conjunto de variáveis, e não por uma alteração de código.** Outro pesquisador reproduz a minha rodada sem tocar no programa — e esse é, para mim, o argumento metodológico mais forte do trabalho."));
corpo.push(fala("A terceira é a instrumentação. Toda execução devolve o tempo de cada etapa separadamente. Sem medir por etapa, não é possível saber onde o custo realmente está."));
corpo.push(fala("A quarta é a verificação, com uma suíte de testes automatizados que usa dublês de modelos, permitindo testar a lógica do pipeline sem carregar os modelos pesados."));
corpo.push(fala("E a quinta é o protocolo experimental, com quatro perfis de áudio. Eles não são arbitrários: cada um estressa uma etapa diferente. O ruído estressa o pré-processamento; múltiplos falantes estressam a segmentação; o silêncio inicial estressa o filtro de atividade de voz."));

// ------------------------------------------------------------------ slide 6
corpo.push(slide("SLIDE 6 · RESULTADOS E DISCUSSÃO — ENTREGA FUNCIONAL", "7:45 – 10:05"));
corpo.push(fala("Passo aos resultados. O resultado primário é um sistema que roda de ponta a ponta — e do qual eu consigo mostrar a saída."));
corpo.push(fala("Ele está acessível por três vias: linha de comando, uma API REST com os endpoints de verificação de saúde e de transcrição, e um painel Streamlit, além de um front-end web. Isso não é conveniência: é a demonstração prática de que o núcleo está isolado, porque a mesma lógica é servida de três formas diferentes."));
corpo.push(rubrica("[Desacelere aqui. Este parágrafo é o coração dos resultados.]"));
corpo.push(fala("Quanto às saídas: a transcrição sai com marcação temporal em cada segmento, no formato horas, minutos e segundos. **Isso é o que torna o resumo auditável: cada afirmação do resumo pode ser rastreada até o minuto do áudio em que foi dita.** É exatamente o que uma ferramenta de caixa-preta não oferece. Além da transcrição, saem os blocos semânticos rotulados, com seus intervalos de tempo, e o resumo em três seções mais a visão geral. Tudo isso em texto, PDF e JSON — e o JSON existe para que outro sistema consuma esse resultado, não apenas uma pessoa."));
corpo.push(fala("Em termos de robustez, implementei validação de upload, com limite de tamanho e de extensões permitidas, e o empacotamento do sistema em contêiner Docker."));
corpo.push(fala("Entreguei também as ferramentas de medição: um script que agrega as métricas de vários áudios em tabela, e outro que faz comparação A/B entre tamanhos do modelo de transcrição. Eles existem para que o resultado não dependa de uma execução isolada."));
corpo.push(fala("Por fim, uma observação de discussão: a modularidade foi testada na prática. Eu troquei a implementação do agrupamento semântico, eliminando uma dependência externa, sem tocar em nenhuma das camadas de interface. Esse é o tipo de evidência que mostra que a separação arquitetural não era apenas uma intenção declarada."));

// ------------------------------------------------------------------ slide 7
corpo.push(slide("SLIDE 7 · RESULTADOS E DISCUSSÃO — CUSTO, ACHADO E LIMITAÇÕES", "10:05 – 12:00"));
corpo.push(fala("Este slide traz o custo computacional por etapa, que é o que a instrumentação permitiu levantar."));
corpo.push(rubrica("[Procedência da tabela: diga isto espontaneamente, antes que perguntem. Vale mais declarar do que ser cobrado.]"));
corpo.push(fala("Uma observação de método antes dos números: as linhas da tabela têm origens diferentes, e isso está declarado na legenda. **O pré-processamento foi medido**, executando a etapa real do pipeline numa CPU de quatro núcleos, sem GPU: custa cerca de um por cento da duração do áudio. **O número de blocos é calculado** dos parâmetros de janela, e não depende de hardware. Os tempos de transcrição e sumarização **são projeções**, e a rodada controlada é o passo imediato do trabalho."));
corpo.push(fala("O que a tabela mostra é que o custo não está distribuído: está concentrado na transcrição."));
corpo.push(rubrica("[Ponto alto do slide. Diga com calma — é um achado seu, não um dado de catálogo.]"));
corpo.push(fala("E daí vem o achado principal. **O custo da transcrição cresce linearmente com a duração da reunião. O da sumarização não cresce**, porque eu limito o contexto em trezentos tokens por seção. A consequência é contraintuitiva: **quanto maior a reunião, melhor o fator de tempo real.** Numa reunião de dois minutos o custo fixo da sumarização domina; numa de dez, ele se dilui."));
corpo.push(fala("Quanto às limitações, começo pela mais específica: abaixo de três minutos a transcrição não chega a quinhentos tokens, então existe uma única janela e o agrupamento não tem o que agrupar. É consequência direta da aritmética do parâmetro que eu escolhi."));
corpo.push(fala("As demais: o agrupamento é guloso, então a ordem de chegada influencia os blocos; o sumarizador é um T5 pequeno, treinado majoritariamente em inglês, e é o gargalo de qualidade — **a transcrição é consistentemente melhor que o resumo, e eu sei por quê**; e não há diarização: o sistema registra o que foi dito, não quem disse."));

// ------------------------------------------------------------------ slide 8
corpo.push(slide("SLIDE 8 · CONSIDERAÇÕES FINAIS", "12:00 – 13:30"));
corpo.push(fala("Voltando ao objetivo do início. Ele foi atingido no nível de sistema: existe um pipeline reprodutível que converte áudio de reunião em português em documentação estruturada e rastreável ao tempo do áudio. No nível da qualidade do resumo, foi atingido parcialmente — e eu sei exatamente onde está o limite."));
corpo.push(fala("A contribuição tem dois diferenciais que quero deixar explícitos. O primeiro é a **auditabilidade**: cada item do resumo volta ao minuto do áudio. O segundo é a **privacidade**: o áudio não sai da máquina onde o sistema roda. Soma-se o protocolo de avaliação, que permite comparar configurações de forma reprodutível, e não apenas relatar uma execução isolada."));
corpo.push(fala("Dos aprendizados, destaco dois: separar o núcleo das interfaces evitou retrabalho ao longo do projeto; e medir por etapa revelou onde o custo estava de verdade."));
corpo.push(fala("Nos trabalhos futuros, a prioridade é um sumarizador instruído em português, porque é o gargalo que os próprios resultados apontaram. Em seguida, diarização de falantes, para atribuir cada decisão a um responsável; agrupamento com otimização global; e avaliação com WER e CER sobre corpus anotado."));
corpo.push(rubrica("[Frase de encerramento. Pausa antes, e olhe para a banca.]"));
corpo.push(fala("Em resumo: **o sistema já transforma reunião falada em documentação rastreável. O próximo passo é elevar a qualidade do resumo ao nível que a transcrição já alcançou.**"));

// ------------------------------------------------------------------ slide 9
corpo.push(slide("SLIDE 9 · REFERÊNCIAS", "13:30 – 13:45"));
corpo.push(rubrica("[Não leia a lista. Uma frase e avance.]"));
corpo.push(fala("O trabalho se apoia em quatro referências centrais: Whisper, para reconhecimento de fala; Sentence-BERT, para representação semântica; T5, para sumarização; e Alemi e Ginsparg, para segmentação textual por embeddings."));

// ----------------------------------------------------------------- slide 10
corpo.push(slide("SLIDE 10 · AGRADECIMENTOS E ENCERRAMENTO", "13:45 – 14:00"));
corpo.push(fala("Agradeço à Universidade Presbiteriana Mackenzie e ao Programa de Iniciação Científica pelo apoio institucional, e ao professor Victor Inácio de Oliveira pela orientação ao longo do projeto."));
corpo.push(fala("Fico à disposição para as perguntas. Muito obrigado."));

// ------------------------------------------------------------------- anexo
corpo.push(new Paragraph({ children: [new PageBreak()] }));
corpo.push(new Paragraph({
  children: [new TextRun({ text: "Anexo — respostas prontas para a arguição", bold: true, color: INK, font: FONT, size: 34 })],
  spacing: { after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 10, space: 8, color: ACCENT } },
}));
corpo.push(new Paragraph({
  children: rt("Não são falas em sequência: são respostas a ter na ponta da língua. Se não souber algo, a resposta forte é “não medi isso; o que eu tenho é X, e o caminho para medir é Y”. Inventar é a única resposta fraca.", { italics: true, color: SOFT, size: 22 }),
  spacing: { before: 140, after: 220, line: 276 },
}));

const qa = [
  ["Esses tempos da tabela foram todos medidos?",
   "O pré-processamento e o número de blocos sim — o pré-processamento executando a etapa real do pipeline, e os blocos por cálculo direto dos parâmetros de janela. Os tempos de transcrição e sumarização são projeção para a mesma classe de hardware; a rodada controlada sobre o conjunto de áudios do protocolo é o passo imediato."],
  ["Por que Whisper e não um serviço comercial de transcrição?",
   "Três razões: o Whisper roda localmente, o que atende ao requisito de privacidade do projeto; tem desempenho documentado em português; e é auditável — eu consigo inspecionar e variar os parâmetros de decodificação, o que um serviço fechado não permite. A arquitetura, aliás, permite trocar o motor de reconhecimento de fala por variável de ambiente."],
  ["Como você escolheu o limiar de 0,78?",
   "É um valor de partida ajustado empiricamente: abaixo dele os blocos ficavam grandes e misturavam assuntos; acima, a transcrição se fragmentava em blocos de uma frase. Não é um ótimo demonstrado — é um parâmetro configurável, e varrê-lo sistematicamente contra uma segmentação de referência é um dos próximos passos."],
  ["Por que agrupamento guloso e não k-means ou hierárquico?",
   "Pelo problema: não sei de antemão quantos assuntos uma reunião tem, o que descarta k-means com k fixo; e a estratégia incremental preserva a ordem temporal da conversa, que é informação relevante aqui. O custo dessa escolha é real e eu o declaro: a ordem de chegada influencia o resultado, porque não há otimização global. Agrupamento hierárquico ou espectral é comparação direta para a próxima etapa."],
  ["O T5 é treinado em inglês. Como ele resume texto em português?",
   "Essa é exatamente a limitação principal do trabalho. O modelo processa o texto, mas a qualidade do resumo fica abaixo da qualidade da transcrição, e isso é consistente nos testes. Por isso a primeira prioridade dos trabalhos futuros é um sumarizador instruído em português, como mT5 ou PTT5, ou um modelo de linguagem com prompt estruturado. A arquitetura já permite essa troca por configuração."],
  ["Qual é o WER do sistema?",
   "Não tenho WER medido, porque ele exige transcrição de referência anotada manualmente, e o protocolo de avaliação prevê isso como etapa seguinte. O que está medido hoje é desempenho — tempo por etapa e fator de tempo real — e qualidade por checklist qualitativo. Prefiro declarar isso a apresentar um número sem referência."],
  ["O sistema funciona em tempo real?",
   "Não é o desenho atual: ele processa gravações, não um fluxo contínuo. O fator de tempo real que eu meço indica o quanto o processamento é mais rápido ou mais lento que a duração do áudio, e depende fortemente do tamanho do modelo e de haver GPU. Transcrição incremental seria uma mudança de arquitetura na etapa de captura."],
  ["Como garantir que o resumo não inventa informação?",
   "Duas salvaguardas. Primeira: o resumo não é gerado sobre a reunião inteira de uma vez, e sim sobre blocos temáticos delimitados, o que restringe o contexto. Segunda, e mais importante: como cada bloco carrega o intervalo de tempo, qualquer afirmação do resumo pode ser conferida contra o trecho correspondente da transcrição. O checklist qualitativo do protocolo tem um item específico para isso."],
  ["Sem diarização, como você sabe quem decidiu o quê?",
   "Não sei — e essa é uma limitação declarada. O sistema registra o que foi dito e quando, não quem disse. Integrar diarização é um trabalho futuro prioritário, justamente porque “decisão sem responsável” é uma informação incompleta para uma ata."],
  ["Qual foi a sua contribuição, já que usou bibliotecas prontas?",
   "As bibliotecas resolvem cada etapa isoladamente; nenhuma delas resolve o problema de ir do áudio à documentação acionável. A contribuição está em três pontos: o encadeamento com remapeamento dos blocos semânticos de volta ao eixo temporal do áudio, que é o que torna o resultado auditável; a arquitetura que isola o núcleo e externaliza a configuração, tornando o experimento reprodutível; e o protocolo de avaliação com a instrumentação que o alimenta."],
  ["Qual hardware é necessário?",
   "Roda em CPU com os modelos pequenos — a configuração padrão usa quantização de 8 bits justamente para isso. GPU reduz substancialmente o tempo de transcrição, que é a etapa dominante. Como o tamanho do modelo é configurável, é possível trocar custo por qualidade conforme a máquina disponível."],
  ["E a LGPD, os dados dos participantes?",
   "É um argumento a favor do desenho adotado: o áudio não sai da máquina onde o sistema roda, então não há transferência para terceiros. O protocolo de avaliação, inclusive, orienta a não versionar áudios reais no repositório."],
  ["Por que janelas de 500 tokens com sobreposição de 50?",
   "A janela precisa ser grande o suficiente para que o vetor represente um assunto, e não uma frase solta; e pequena o suficiente para que dois assuntos não caiam na mesma janela. A sobreposição de 10% evita que uma ideia seja cortada exatamente na fronteira. Ambos são configuráveis e entram na mesma varredura de parâmetros que mencionei no limiar."],
];
qa.forEach(([q, a]) => { corpo.push(pergunta(q)); corpo.push(resposta(a)); });

const doc = new Document({
  creator: "Matheus Barbosa Meloni",
  title: "Falas da apresentação — XXII Jornada de Iniciação Científica",
  styles: { default: { document: { run: { font: FONT, size: 26, color: INK } } } },
  sections: [{
    properties: { page: { margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
    children: corpo,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(process.argv[2], buf);
  console.log("gerado:", process.argv[2], buf.length, "bytes");
});
