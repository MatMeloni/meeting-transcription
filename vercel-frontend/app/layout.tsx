import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ata de Reunião – Transcrição Automática",
  description: "Grave, transcreva e gere a ata da sua reunião automaticamente.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
