"""Figuras para o banner do VIII SIMAC."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

OUT = "/home/user/meeting-transcription/docs/apresentacao/figuras/"
AZUL, LARANJA = "#005AAB", "#C85200"
INK, MUTED, GRID = "#1A1A1A", "#5A6570", "#D8DDE2"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "axes.edgecolor": MUTED, "axes.linewidth": 1.0,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "savefig.facecolor": "white", "figure.facecolor": "white",
})

# ----------------------------------------------------------- Figura: custo
dur = np.array([2, 5, 10])                 # minutos
tr_lo, tr_hi = np.array([20, 45, 90]), np.array([40, 105, 210])
su_lo, su_hi = np.array([25, 25, 25]), np.array([50, 50, 50])
tr_mid, su_mid = (tr_lo + tr_hi) / 2, (su_lo + su_hi) / 2

fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=200)
ax.fill_between(dur, tr_lo, tr_hi, color=AZUL, alpha=0.16, linewidth=0)
ax.fill_between(dur, su_lo, su_hi, color=LARANJA, alpha=0.16, linewidth=0)
ax.plot(dur, tr_mid, color=AZUL, lw=2.6, marker="o", ms=9,
        mfc="white", mew=2.4, mec=AZUL, label="Transcrição (ASR)", zorder=3)
ax.plot(dur, su_mid, color=LARANJA, lw=2.6, marker="s", ms=9,
        mfc="white", mew=2.4, mec=LARANJA, label="Sumarização", zorder=3)

ax.annotate("cresce linearmente\ncom a duração", xy=(10, 150), xytext=(6.4, 186),
            color=AZUL, fontsize=15, fontweight="bold", ha="center", va="center")
ax.annotate("custo constante\n(contexto truncado)", xy=(10, 37), xytext=(6.6, 72),
            color=LARANJA, fontsize=15, fontweight="bold", ha="center", va="center")

ax.set_xlabel("Duração do áudio (min)", fontsize=17, labelpad=9)
ax.set_ylabel("Tempo de processamento (s)", fontsize=17, labelpad=9)
ax.set_xticks(dur); ax.set_xticklabels([f"{d}" for d in dur], fontsize=16)
ax.tick_params(axis="y", labelsize=16)
ax.set_xlim(1.2, 11.2); ax.set_ylim(0, 225)
ax.yaxis.grid(True, color=GRID, lw=1.0); ax.set_axisbelow(True)
ax.xaxis.grid(False)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
leg = ax.legend(fontsize=16, frameon=False, loc="upper left", handlelength=1.8)
for t in leg.get_texts():
    t.set_color(INK)
fig.tight_layout(pad=0.6)
fig.savefig(OUT + "custo_por_etapa.png", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------ Figura: banda telefônica
fig, ax = plt.subplots(figsize=(9.4, 3.5), dpi=200)
ax.add_patch(Rectangle((0, 0.56), 8000, 0.30, facecolor=AZUL, alpha=0.18,
                       edgecolor=AZUL, lw=1.6))
ax.text(4000, 0.71, "Banda larga — esperada pelo reconhecedor (16 kHz)",
        ha="center", va="center", fontsize=15, color=AZUL, fontweight="bold")

ax.add_patch(Rectangle((300, 0.12), 3100, 0.30, facecolor=LARANJA, alpha=0.30,
                       edgecolor=LARANJA, lw=1.6))
ax.text(1850, 0.27, "Banda telefônica\n300–3.400 Hz", ha="center", va="center",
        fontsize=15, color=LARANJA, fontweight="bold")
ax.add_patch(Rectangle((3400, 0.12), 4600, 0.30, facecolor="none",
                       edgecolor=MUTED, lw=1.4, hatch="///", alpha=0.55))
ax.text(5700, 0.27, "conteúdo ausente —\nnão recuperável por reamostragem",
        ha="center", va="center", fontsize=14, color=MUTED, style="italic")

ax.annotate("", xy=(8000, 0.02), xytext=(4000, 0.02),
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2))
ax.text(6000, -0.05, "fricativas /s/, /ʃ/, /f/ concentram energia nesta faixa",
        ha="center", va="top", fontsize=13.5, color=MUTED)

ax.set_xlim(-150, 8250); ax.set_ylim(-0.16, 0.95)
ax.set_xticks([0, 2000, 4000, 6000, 8000])
ax.set_xticklabels(["0", "2 k", "4 k", "6 k", "8 kHz"], fontsize=15)
ax.set_yticks([])
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.set_xlabel("Frequência", fontsize=16, labelpad=8)
fig.tight_layout(pad=0.6)
fig.savefig(OUT + "banda_telefonica.png", bbox_inches="tight")
plt.close(fig)
print("figuras geradas")
