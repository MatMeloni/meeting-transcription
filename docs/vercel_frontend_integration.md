# Integração do Front-end na Vercel

Este guia descreve como conectar um front-end (Next.js/React) hospedado na Vercel ao backend de transcrição implantado via Docker em um provedor como Railway, Render ou Fly.io.

## 1. Preparar o backend

1. Faça deploy do container usando o `Dockerfile` deste projeto.
2. Garanta que o serviço esteja exposto em HTTPS e acessível publicamente (ex.: `https://meeting-api.example.com`).
3. Configure armazenamento persistente para `/app/outputs` se quiser manter os relatórios.
4. Ajuste variáveis de ambiente, se necessário, diretamente no painel do provedor (ex.: `WHISPER_MODEL_SIZE`, `SUMMARY_MAX_TOKENS`).

## 2. Configurar o projeto Next.js

1. Crie um projeto na Vercel (ou use um existente).
2. Defina a variável de ambiente `NEXT_PUBLIC_MEETING_API` apontando para a URL pública do backend.
3. Confirme que o backend permite CORS (já ativado em `src/app.py`).

### Upload de arquivo

Exemplo de componente Next.js para envio de áudio e exibição do resumo:

```tsx
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_MEETING_API ?? "";

export function MeetingUploader() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/transcribe`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Falha ao processar áudio");
      }
      const payload = await response.json();
      setSummary(payload.summary);
    } catch (error) {
      console.error(error);
      alert("Erro ao processar reunião");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleUpload} encType="multipart/form-data">
      <input type="file" name="file" accept=".wav,.mp3,.m4a" required />
      <input type="text" name="meeting_name" placeholder="Nome da reunião" />
      <button type="submit" disabled={loading}>
        {loading ? "Processando..." : "Enviar áudio"}
      </button>
      {summary && (
        <pre>{JSON.stringify(summary, null, 2)}</pre>
      )}
    </form>
  );
}
```

Inclua esse componente em uma página (`pages/index.tsx`) e publique.

### Proxy opcional

Se desejar, crie um *API route* em Next.js (`pages/api/transcribe.ts`) para atuar como proxy, escondendo a URL real do backend e permitindo autenticação:

```ts
import type { NextApiRequest, NextApiResponse } from "next";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Método não suportado" });
    return;
  }

  const apiUrl = process.env.MEETING_API_INTERNAL;
  if (!apiUrl) {
    res.status(500).json({ error: "MEETING_API_INTERNAL não definido" });
    return;
  }

  const response = await fetch(`${apiUrl}/transcribe`, {
    method: "POST",
    body: req,
    headers: {
      ...req.headers,
    },
  });

  res.status(response.status).send(await response.text());
}
```

Na Vercel, defina `MEETING_API_INTERNAL` como a URL do backend.

## 3. Demonstração de “tempo real”

O backend atual processa o áudio após o upload completo. Para uma experiência próxima ao tempo real:

1. Grave pequenos trechos (por exemplo, 15 s) no navegador usando a Web Audio API.
2. Envie cada bloco ao backend (chunk upload) e agregue a transcrição retornada.
3. Atualize o front com o resumo parcial a cada resposta.

Caso precise streaming verdadeiro, será necessário estender o backend com WebSockets e pipeline incremental.

## 4. Downloads de relatórios

O backend retorna caminhos locais. Para disponibilizá-los na Vercel:

- Crie endpoints adicionais no backend que sirvam os arquivos (ex.: `/download/transcript/pdf?meeting=...`).
- Ou replique os arquivos em um storage (S3/R2) no final do processamento e retorne URLs públicas.

## 5. Publicação

1. Faça deploy do backend primeiro e valide o endpoint `/health`.
2. Ajuste variáveis de ambiente na Vercel e execute `vercel --prod`.
3. Teste o fluxo completo com um áudio curto antes da demonstração.
