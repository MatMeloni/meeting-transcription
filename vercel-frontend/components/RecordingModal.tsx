"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { AudioSources } from "@/app/page";

type Status = "recording" | "processing" | "done" | "error";

type Summary = {
  overview: string[];
  decisions: string[];
  pending: string[];
  next_steps: string[];
};

type Props = {
  sources: AudioSources;
  onClose: () => void;
};

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");
const LIVE_INTERVAL_MS = 60_000; // send chunk every 60 s for live transcript

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = (seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function RecordingModal({ sources, onClose }: Props) {
  const [status, setStatus] = useState<Status>("recording");
  const [elapsed, setElapsed] = useState(0);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [fullTranscript, setFullTranscript] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [showTranscript, setShowTranscript] = useState(false);
  const [meetingName, setMeetingName] = useState("Reunião");

  const recorderRef = useRef<MediaRecorder | null>(null);
  const allChunksRef = useRef<Blob[]>([]);
  const mimeRef = useRef("audio/webm");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const liveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll live transcript
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [liveTranscript]);

  const sendForTranscription = useCallback(
    async (chunks: Blob[], final: boolean): Promise<{ transcript_text?: string; summary?: Summary }> => {
      const blob = new Blob(chunks, { type: mimeRef.current });
      const ext = mimeRef.current.includes("ogg") ? ".ogg" : ".webm";
      const fd = new FormData();
      fd.append("file", blob, `recording${ext}`);
      const url = `${API_URL}/transcribe?meeting_name=${encodeURIComponent(meetingName)}`;
      const res = await fetch(url, { method: "POST", body: fd });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`API ${res.status}: ${detail}`);
      }
      return res.json();
    },
    [meetingName]
  );

  const stopRecording = useCallback(async () => {
    clearInterval(timerRef.current!);
    clearInterval(liveTimerRef.current!);

    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      await new Promise<void>((resolve) => {
        recorder.onstop = () => resolve();
        recorder.stop();
      });
    }

    // Stop all media tracks
    sources.streams.forEach((s) => s.getTracks().forEach((t) => t.stop()));
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
    }

    setStatus("processing");

    try {
      const data = await sendForTranscription(allChunksRef.current, true);
      setFullTranscript(data.transcript_text ?? "");
      setSummary((data as any).summary ?? null);
      setStatus("done");
    } catch (e: any) {
      setErrorMsg(e.message ?? "Erro ao processar áudio.");
      setStatus("error");
    }
  }, [sources, sendForTranscription]);

  // Start recording on mount
  useEffect(() => {
    let cancelled = false;

    const start = async () => {
      const ctx = new AudioContext();
      audioCtxRef.current = ctx;
      const destination = ctx.createMediaStreamDestination();

      sources.streams.forEach((stream) => {
        if (stream.getAudioTracks().length > 0) {
          ctx.createMediaStreamSource(stream).connect(destination);
        }
      });

      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")
        ? "audio/ogg;codecs=opus"
        : "audio/webm";

      mimeRef.current = mime.split(";")[0];

      const recorder = new MediaRecorder(destination.stream, { mimeType: mime });
      recorderRef.current = recorder;
      allChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) allChunksRef.current.push(e.data);
      };

      recorder.start(1000);

      // Elapsed timer
      timerRef.current = setInterval(() => {
        if (!cancelled) setElapsed((t) => t + 1);
      }, 1000);

      // Live transcript every 60 s
      liveTimerRef.current = setInterval(async () => {
        if (cancelled || allChunksRef.current.length === 0) return;
        try {
          const data = await sendForTranscription(allChunksRef.current, false);
          if (!cancelled && data.transcript_text) {
            setLiveTranscript(data.transcript_text);
          }
        } catch {
          // silently ignore live update failures
        }
      }, LIVE_INTERVAL_MS);
    };

    start();

    return () => {
      cancelled = true;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle stream end by external action (e.g. user stops screen share)
  useEffect(() => {
    sources.streams.forEach((stream) => {
      stream.getTracks().forEach((track) => {
        track.onended = () => {
          if (status === "recording") stopRecording();
        };
      });
    });
  }, [sources, status, stopRecording]);

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.9)", backdropFilter: "blur(16px)" }}
    >
      {status === "recording" && (
        <RecordingView
          elapsed={elapsed}
          liveTranscript={liveTranscript}
          transcriptEndRef={transcriptEndRef}
          onStop={stopRecording}
          meetingName={meetingName}
          setMeetingName={setMeetingName}
        />
      )}

      {status === "processing" && <ProcessingView elapsed={elapsed} />}

      {status === "done" && summary && (
        <SummaryView
          summary={summary}
          fullTranscript={fullTranscript}
          showTranscript={showTranscript}
          setShowTranscript={setShowTranscript}
          onClose={onClose}
          meetingName={meetingName}
        />
      )}

      {status === "error" && (
        <ErrorView message={errorMsg} onClose={onClose} />
      )}
    </div>
  );
}

// ── Sub-views ──────────────────────────────────────────────────────────────

function RecordingView({
  elapsed,
  liveTranscript,
  transcriptEndRef,
  onStop,
  meetingName,
  setMeetingName,
}: {
  elapsed: number;
  liveTranscript: string;
  transcriptEndRef: React.RefObject<HTMLDivElement>;
  onStop: () => void;
  meetingName: string;
  setMeetingName: (v: string) => void;
}) {
  return (
    <div className="w-full max-w-2xl flex flex-col gap-6 animate-fadein">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
          <span className="text-red-400 font-medium text-sm uppercase tracking-widest">
            Gravando
          </span>
        </div>
        <span className="text-2xl font-mono text-white">{formatTime(elapsed)}</span>
      </div>

      {/* Meeting name */}
      <input
        value={meetingName}
        onChange={(e) => setMeetingName(e.target.value)}
        placeholder="Nome da reunião"
        className="glass rounded-lg px-4 py-2 text-white placeholder-slate-500 text-sm w-full focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />

      {/* Waveform */}
      <div className="glass rounded-2xl p-6 flex items-center justify-center gap-1.5 h-24">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="wave-bar animate-wave"
            style={{
              height: `${24 + Math.random() * 20}px`,
              animationDelay: `${(i * 0.06).toFixed(2)}s`,
            }}
          />
        ))}
      </div>

      {/* Live transcript */}
      <div className="glass rounded-2xl p-5 h-48 overflow-y-auto">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-3">
          Transcrição ao vivo
          {!liveTranscript && (
            <span className="ml-2 text-slate-600">
              — aparece após o primeiro minuto
            </span>
          )}
        </p>
        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
          {liveTranscript || ""}
        </p>
        <div ref={transcriptEndRef} />
      </div>

      {/* Stop button */}
      <button
        onClick={onStop}
        className="w-full py-4 rounded-2xl font-semibold text-white text-lg transition-all hover:brightness-110 active:scale-95"
        style={{
          background: "linear-gradient(135deg, #ef4444, #dc2626)",
          boxShadow: "0 4px 32px rgba(239,68,68,0.4)",
        }}
      >
        ⏹ Parar e gerar ATA
      </button>
    </div>
  );
}

function ProcessingView({ elapsed }: { elapsed: number }) {
  return (
    <div className="flex flex-col items-center gap-6 animate-fadein">
      <div
        className="w-20 h-20 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin"
      />
      <div className="text-center">
        <p className="text-white font-semibold text-lg">Processando reunião…</p>
        <p className="text-slate-400 text-sm mt-1">
          {formatTime(elapsed)} de áudio gravado · transcrevendo e gerando ATA
        </p>
      </div>
    </div>
  );
}

function SummaryView({
  summary,
  fullTranscript,
  showTranscript,
  setShowTranscript,
  onClose,
  meetingName,
}: {
  summary: Summary;
  fullTranscript: string;
  showTranscript: boolean;
  setShowTranscript: (v: boolean) => void;
  onClose: () => void;
  meetingName: string;
}) {
  const handleDownload = () => {
    const lines = [
      `ATA DA REUNIÃO — ${meetingName}`,
      `Data: ${new Date().toLocaleDateString("pt-BR")}`,
      "",
      "VISÃO GERAL",
      ...summary.overview.map((l) => `  ${l}`),
      "",
      "DECISÕES",
      ...summary.decisions.map((l) => `  • ${l}`),
      "",
      "PENDÊNCIAS",
      ...summary.pending.map((l) => `  • ${l}`),
      "",
      "PRÓXIMOS PASSOS",
      ...summary.next_steps.map((l) => `  • ${l}`),
      "",
      "TRANSCRIÇÃO COMPLETA",
      fullTranscript,
    ].join("\n");

    const blob = new Blob([lines], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ata-${meetingName.replace(/\s+/g, "-").toLowerCase()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-2xl flex flex-col gap-5 animate-fadein max-h-[90dvh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between sticky top-0 pt-2 pb-4 z-10"
        style={{ background: "rgba(0,0,0,0.85)", backdropFilter: "blur(12px)" }}>
        <div>
          <h2 className="text-2xl font-bold gradient-text">ATA da Reunião</h2>
          <p className="text-slate-400 text-sm">{meetingName} · {new Date().toLocaleDateString("pt-BR")}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleDownload}
            className="glass px-4 py-2 rounded-xl text-sm hover:bg-white/10 transition-colors"
          >
            ⬇ Baixar
          </button>
          <button
            onClick={onClose}
            className="glass px-4 py-2 rounded-xl text-sm hover:bg-white/10 transition-colors"
          >
            ✕ Fechar
          </button>
        </div>
      </div>

      {/* Overview */}
      {summary.overview.length > 0 && (
        <Section emoji="📋" title="Visão Geral" color="indigo">
          {summary.overview.map((item, i) => (
            <p key={i} className="text-slate-300 text-sm leading-relaxed">{item}</p>
          ))}
        </Section>
      )}

      {/* Decisions */}
      {summary.decisions.length > 0 && (
        <Section emoji="✅" title="Decisões" color="emerald">
          <ul className="space-y-2">
            {summary.decisions.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="text-emerald-400 mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Pending */}
      {summary.pending.length > 0 && (
        <Section emoji="⏳" title="Pendências" color="amber">
          <ul className="space-y-2">
            {summary.pending.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="text-amber-400 mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Next steps */}
      {summary.next_steps.length > 0 && (
        <Section emoji="🚀" title="Próximos Passos" color="purple">
          <ul className="space-y-2">
            {summary.next_steps.map((item, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-300">
                <span className="text-purple-400 mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Full transcript toggle */}
      <button
        onClick={() => setShowTranscript(!showTranscript)}
        className="glass rounded-xl px-4 py-3 text-sm text-slate-400 hover:text-white transition-colors text-left"
      >
        {showTranscript ? "▲ Ocultar transcrição completa" : "▼ Ver transcrição completa"}
      </button>

      {showTranscript && fullTranscript && (
        <div className="glass rounded-xl p-5 max-h-60 overflow-y-auto">
          <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
            {fullTranscript}
          </p>
        </div>
      )}

      {/* New recording button */}
      <button
        onClick={onClose}
        className="w-full py-3 rounded-xl font-semibold text-white transition-all hover:brightness-110 active:scale-95 mb-4"
        style={{ background: "linear-gradient(135deg, #6366f1, #a855f7)" }}
      >
        + Nova Gravação
      </button>
    </div>
  );
}

function Section({
  emoji,
  title,
  color,
  children,
}: {
  emoji: string;
  title: string;
  color: "indigo" | "emerald" | "amber" | "purple";
  children: React.ReactNode;
}) {
  const borderColor = {
    indigo: "border-indigo-500/40",
    emerald: "border-emerald-500/40",
    amber: "border-amber-500/40",
    purple: "border-purple-500/40",
  }[color];

  return (
    <div className={`glass rounded-xl p-5 border-l-2 ${borderColor}`}>
      <h3 className="font-semibold mb-3 flex items-center gap-2">
        <span>{emoji}</span>
        <span>{title}</span>
      </h3>
      {children}
    </div>
  );
}

function ErrorView({ message, onClose }: { message: string; onClose: () => void }) {
  return (
    <div className="glass rounded-2xl p-8 w-full max-w-md animate-fadein text-center">
      <p className="text-4xl mb-4">⚠️</p>
      <h2 className="text-xl font-semibold text-red-400 mb-2">Erro ao processar</h2>
      <p className="text-slate-400 text-sm mb-6 whitespace-pre-wrap">{message}</p>
      <button
        onClick={onClose}
        className="px-6 py-3 rounded-xl glass hover:bg-white/10 transition-colors"
      >
        Fechar
      </button>
    </div>
  );
}
