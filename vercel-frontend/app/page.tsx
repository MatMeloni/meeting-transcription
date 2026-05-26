"use client";

import { useState } from "react";
import AudioSourceModal from "@/components/AudioSourceModal";
import RecordingModal from "@/components/RecordingModal";

export type AudioSources = {
  mic: boolean;
  system: boolean;
  streams: MediaStream[];
};

export default function Home() {
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [activeSources, setActiveSources] = useState<AudioSources | null>(null);

  const handleSourceConfirmed = (sources: AudioSources) => {
    setShowSourceModal(false);
    setActiveSources(sources);
  };

  const handleRecordingDone = () => {
    setActiveSources(null);
  };

  return (
    <main className="relative flex flex-col items-center justify-center min-h-dvh overflow-hidden px-4">
      {/* Background decoration */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.18) 0%, transparent 70%), radial-gradient(ellipse 50% 40% at 80% 80%, rgba(168,85,247,0.12) 0%, transparent 70%)",
        }}
      />

      {/* Header */}
      <div className="text-center mb-12 animate-fadein">
        <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 text-sm text-slate-400 mb-6">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Powered by Whisper AI
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-3">
          <span className="gradient-text">Ata de Reunião</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-md mx-auto">
          Grave, transcreva e gere a ata automaticamente — tudo no navegador.
        </p>
      </div>

      {/* Play button */}
      <button
        onClick={() => setShowSourceModal(true)}
        className="relative group focus:outline-none animate-fadein"
        style={{ animationDelay: "0.15s" }}
        aria-label="Iniciar gravação"
      >
        {/* Pulse ring */}
        <span
          aria-hidden
          className="absolute inset-0 rounded-full animate-pulse_ring"
          style={{
            background: "linear-gradient(135deg, #6366f1, #a855f7)",
            filter: "blur(2px)",
          }}
        />

        {/* Button circle */}
        <span
          className="relative flex items-center justify-center w-28 h-28 rounded-full shadow-2xl transition-transform duration-200 group-hover:scale-105 group-active:scale-95"
          style={{
            background: "linear-gradient(135deg, #6366f1, #a855f7)",
            boxShadow: "0 0 60px rgba(99,102,241,0.5)",
          }}
        >
          {/* Play icon */}
          <svg
            viewBox="0 0 24 24"
            fill="white"
            className="w-12 h-12 ml-1"
            aria-hidden
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        </span>
      </button>

      <p className="mt-6 text-slate-500 text-sm animate-fadein" style={{ animationDelay: "0.25s" }}>
        Clique para iniciar a gravação da reunião
      </p>

      {/* Features row */}
      <div
        className="flex flex-wrap gap-4 mt-16 text-slate-500 text-xs justify-center animate-fadein"
        style={{ animationDelay: "0.35s" }}
      >
        {["🎤 Microfone", "💻 Som do computador", "📝 Transcrição ao vivo", "📋 ATA automática"].map(
          (f) => (
            <span key={f} className="glass rounded-full px-3 py-1">
              {f}
            </span>
          )
        )}
      </div>

      {/* Modals */}
      {showSourceModal && (
        <AudioSourceModal
          onConfirm={handleSourceConfirmed}
          onCancel={() => setShowSourceModal(false)}
        />
      )}

      {activeSources && (
        <RecordingModal sources={activeSources} onClose={handleRecordingDone} />
      )}
    </main>
  );
}
