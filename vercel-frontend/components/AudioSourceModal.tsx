"use client";

import { useState } from "react";
import type { AudioSources } from "@/app/page";

type Props = {
  onConfirm: (sources: AudioSources) => void;
  onCancel: () => void;
};

export default function AudioSourceModal({ onConfirm, onCancel }: Props) {
  const [useMic, setUseMic] = useState(true);
  const [useSystem, setUseSystem] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    if (!useMic && !useSystem) {
      setError("Selecione pelo menos uma fonte de áudio.");
      return;
    }
    setError("");
    setLoading(true);
    const streams: MediaStream[] = [];

    try {
      if (useMic) {
        const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streams.push(micStream);
      }

      if (useSystem) {
        try {
          const displayStream = await navigator.mediaDevices.getDisplayMedia({
            audio: {
              echoCancellation: false,
              noiseSuppression: false,
              sampleRate: 44100,
            } as MediaTrackConstraints,
            video: true,
          });
          // Stop video tracks immediately — we only need audio
          displayStream.getVideoTracks().forEach((t) => t.stop());
          streams.push(displayStream);
        } catch (e) {
          if (streams.length === 0) {
            setError("Não foi possível acessar o áudio do sistema. Tente apenas o microfone.");
            setLoading(false);
            return;
          }
          // If mic is selected too, just warn and continue
          setError("Áudio do sistema indisponível; gravando apenas microfone.");
        }
      }

      onConfirm({ mic: useMic, system: useSystem, streams });
    } catch (e) {
      setError("Permissão de áudio negada. Verifique as configurações do navegador.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.75)", backdropFilter: "blur(8px)" }}
    >
      <div className="glass rounded-2xl p-8 w-full max-w-md animate-fadein shadow-2xl">
        <h2 className="text-xl font-semibold mb-1">Selecionar fontes de áudio</h2>
        <p className="text-slate-400 text-sm mb-6">
          Escolha o que será gravado e transcrito.
        </p>

        <div className="space-y-3 mb-8">
          <SourceCard
            icon="🎤"
            title="Microfone"
            description="Captura sua voz via microfone"
            checked={useMic}
            onChange={setUseMic}
          />
          <SourceCard
            icon="💻"
            title="Som do computador"
            description="Captura áudio de chamadas, vídeos ou apps. O navegador pedirá para compartilhar a tela — marque 'Compartilhar áudio'."
            checked={useSystem}
            onChange={setUseSystem}
          />
        </div>

        {error && (
          <p className="text-amber-400 text-sm mb-4 glass rounded-lg px-3 py-2">
            ⚠️ {error}
          </p>
        )}

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-3 rounded-xl text-slate-400 glass hover:text-white transition-colors"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            onClick={handleStart}
            disabled={loading || (!useMic && !useSystem)}
            className="flex-1 px-4 py-3 rounded-xl font-semibold text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 active:scale-95"
            style={{
              background: "linear-gradient(135deg, #6366f1, #a855f7)",
              boxShadow: "0 4px 24px rgba(99,102,241,0.4)",
            }}
          >
            {loading ? "Aguardando permissão…" : "▶ Iniciar Gravação"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SourceCard({
  icon,
  title,
  description,
  checked,
  onChange,
}: {
  icon: string;
  title: string;
  description: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`w-full text-left rounded-xl p-4 border transition-all duration-200 flex gap-4 items-start ${
        checked
          ? "border-indigo-500 bg-indigo-500/10"
          : "border-white/10 bg-white/[0.03] hover:bg-white/[0.06]"
      }`}
    >
      <span className="text-2xl mt-0.5 shrink-0">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium">{title}</span>
          <span
            className={`w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center transition-colors ${
              checked ? "border-indigo-400 bg-indigo-500" : "border-slate-600"
            }`}
          >
            {checked && (
              <svg viewBox="0 0 12 12" fill="white" className="w-3 h-3">
                <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round" />
              </svg>
            )}
          </span>
        </div>
        <p className="text-slate-400 text-xs mt-1 leading-relaxed">{description}</p>
      </div>
    </button>
  );
}
