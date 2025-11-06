# Integração do Front-end na Vercel

Guia para conectar um front-end (Next.js/React) hospedado na Vercel ao backend de transcrição implantado via Docker em provedores como Railway, Render ou Fly.io.

## 1. Preparar o backend

1. Publique o container produzido pelo `Dockerfile`.
2. Garanta que o serviço esteja exposto em HTTPS (ex.: `https://meeting-api.example.com`).
3. Configure armazenamento persistente para `/app/src/outputs` caso queira manter relatórios.
4. Ajuste variáveis de ambiente no painel do provedor (ex.: `WHISPER_MODEL`, `SUMMARY_MAX_TOKENS`).

## 2. Configurar o projeto Next.js

1. Crie um projeto na Vercel (ou use um existente).
2. Defina a variável `NEXT_PUBLIC_MEETING_API` apontando para a URL pública do backend.
3. Confirme que o backend permite CORS (já habilitado em `backend/api/app.py`).

### Upload de arquivo

Componente Next.js de exemplo:

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
      {summary && <pre>{JSON.stringify(summary, null, 2)}</pre>}
    </form>
  );
}
```

### Proxy opcional

API route em Next.js para esconder a URL do backend:

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

Na Vercel, defina `MEETING_API_INTERNAL` como a URL interna do backend.

## 3. Demonstração quase em tempo real

O backend atual processa o áudio após o upload completo. Para simular tempo real:

1. Grave blocos curtos (ex.: 15 s) no navegador com Web Audio API.
2. Envie cada bloco sequencialmente ao backend.
3. Atualize o front-end com a resposta de cada requisição, agregando transcrição e resumo incremental.

Para streaming verdadeiro, será necessário estender o backend com WebSockets e um pipeline incremental.

## 4. Downloads de relatórios

O backend retorna caminhos locais. Para disponibilizar os arquivos na web:

- Crie endpoints adicionais no backend que sirvam os PDFs/JSON gerados.
- Ou envie os arquivos para um storage (S3/R2) e retorne URLs públicas.

## 5. Publicação

1. Faça deploy do backend e valide o endpoint `/health`.
2. Configure as variáveis de ambiente na Vercel e execute `vercel --prod`.
3. Teste o fluxo completo com um áudio curto antes da demonstração oficial.
