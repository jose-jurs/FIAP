"""
Gera os gráficos do README do ColheitaCerta (assets/graficos/*.png).

Uso:  python scripts/gerar_graficos.py
Dependência: matplotlib (só para este script; o sistema principal usa apenas oracledb).

Todos os números vêm do roteiro de demonstração e das fontes citadas no README:
- Conab, 2º levantamento safra 2026/27 (20/08/2026): 705,2 milhões t
- AFCP-PE: R$ 139,27/t (agosto/2026) e R$ 144,18/t (estimativa setembro/2026)
- CNA/Senar/Cepea (citado pela AFCP): custo de produção R$ 215/t (base safra 2025/26)
- IAC (via Canal Rural): perdas até 15% na colheita mecanizada e ~5% na manual
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator

SAIDA = Path(__file__).resolve().parent.parent / "assets" / "graficos"
SAIDA.mkdir(parents=True, exist_ok=True)

# ---------------- paleta (superfície clara) ----------------
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
AZUL = "#2a78d6"
AZUL_CLARO = "#b7d3f6"
CINZA = "#c3c2b7"
BOM, ALERTA, CRITICO = "#0ca30c", "#fab219", "#d03b3b"

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"],
    "font.size": 11,
    "axes.edgecolor": EIXO,
    "axes.labelcolor": TINTA_2,
    "xtick.color": MUDO,
    "ytick.color": MUDO,
    "axes.facecolor": SUPERFICIE,
    "figure.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ---------------- dados ----------------
PROD_THA = 85.0          # produtividade colhida (t/ha)
AREA_HA = 100.0          # área colhida (ha)
AREA_AMOSTRA = 10.0      # m²
PRECO = 144.18           # R$/t, AFCP-PE set/2026
PRECO_AGO = 139.27       # R$/t, AFCP-PE ago/2026
CUSTO = 215.0            # R$/t, CNA/Senar/Cepea (base 2025/26)
META = 0.05
PRODUCAO_BR = 705.2      # milhões t, Conab 20/08/2026

AMOSTRA = {"Rebolos": 3.1, "Cana inteira": 2.5, "Tocos": 1.2, "Lascas": 0.4}


def brl(v, casas=2):
    s = f"{v:,.{casas}f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def num(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


kg = sum(AMOSTRA.values())
perda_tha = kg / AREA_AMOSTRA * 10
perda_pct = perda_tha / (PROD_THA + perda_tha)
t_perdidas = perda_tha * AREA_HA
prejuizo = t_perdidas * PRECO
meta_tha = META * PROD_THA / (1 - META)
recuperavel_t = (perda_tha - meta_tha) * AREA_HA
recuperavel = recuperavel_t * PRECO
prejuizo_meta = prejuizo - recuperavel


def salvar(fig, nome):
    fig.savefig(SAIDA / nome, dpi=200, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("gerado:", SAIDA / nome)


def grade_y(ax):
    ax.yaxis.grid(True, color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def titulo(ax, t, sub=None):
    ax.set_title(t, loc="left", fontsize=14, fontweight="bold", color=TINTA, pad=26 if sub else 12)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color=TINTA_2, va="bottom")


# =====================================================================
# 1) DASHBOARD DO EXEMPLO
# =====================================================================
def dashboard():
    fig = plt.figure(figsize=(13, 8.2))
    fig.text(0.04, 0.955, "ColheitaCerta · Painel do talhão T-001", fontsize=19,
             fontweight="bold", color=TINTA)
    fig.text(0.04, 0.918, "Colheita mecânica · 100 ha colhidos · 85 t/ha · amostra de 10 m² · "
             "preço AFCP-PE set/2026 (R$ 144,18/t)", fontsize=11, color=TINTA_2)

    # --- KPIs ---
    kpis = [
        ("Perda", f"{num(perda_tha)} t/ha", "7,2 kg em 10 m²"),
        ("Perda sobre a produção", f"{num(perda_pct*100)}%", "nível MÉDIO"),
        ("Cana deixada no campo", f"{num(t_perdidas, 0)} t", "no talhão de 100 ha"),
        ("Prejuízo", brl(prejuizo), f"recuperável na meta: {brl(recuperavel, 0)}"),
    ]
    w, h, y0, gap = 0.215, 0.15, 0.715, 0.017
    for i, (rot, val, nota) in enumerate(kpis):
        x0 = 0.04 + i * (w + gap)
        ax = fig.add_axes([x0, y0, w, h])
        ax.set_axis_off()
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.06",
                                    transform=ax.transAxes, facecolor="white",
                                    edgecolor=GRADE, linewidth=1.2))
        ax.text(0.07, 0.76, rot, fontsize=10.5, color=TINTA_2, transform=ax.transAxes)
        ax.text(0.07, 0.38, val, fontsize=21, fontweight="bold", color=TINTA, transform=ax.transAxes)
        ax.text(0.07, 0.12, nota, fontsize=9.5,
                color=ALERTA if "MÉDIO" in nota else MUDO,
                fontweight="bold" if "MÉDIO" in nota else "normal",
                transform=ax.transAxes)

    # --- faixa de classificação ---
    ax = fig.add_axes([0.04, 0.53, 0.92, 0.1])
    faixas = [(0, 5, BOM, "BAIXA  ≤ 5%"), (5, 10, ALERTA, "MÉDIA  5–10%"), (10, 20, CRITICO, "ALTA  > 10%")]
    for a, b, c, r in faixas:
        ax.barh(0, b - a, left=a, height=0.5, color=c, alpha=0.9, edgecolor=SUPERFICIE, linewidth=2)
        ax.text((a + b) / 2, -0.55, r, ha="center", va="top", fontsize=10, color=TINTA_2)
    v = perda_pct * 100
    ax.plot([v, v], [-0.35, 0.42], color=TINTA, linewidth=2.5)
    ax.plot(v, 0.42, marker="v", markersize=11, color=TINTA)
    ax.text(v, 0.78, f"Talhão T-001: {num(v)}%", ha="center", fontsize=11, fontweight="bold", color=TINTA)
    ax.plot([15, 15], [-0.25, 0.25], color="white", linewidth=1.5, linestyle=(0, (2, 2)))
    ax.text(15, 0.36, "máx. mecanizada (IAC) 15%", ha="center", fontsize=8.5, color=TINTA_2)
    ax.set_xlim(0, 20); ax.set_ylim(-1.1, 1.05); ax.set_axis_off()
    fig.text(0.04, 0.655, "Classificação da perda (%)", fontsize=12, fontweight="bold", color=TINTA)

    # --- composição ---
    ax = fig.add_axes([0.13, 0.07, 0.33, 0.33])
    nomes = list(AMOSTRA)[::-1]
    vals = [AMOSTRA[n] for n in nomes]
    cores = [AZUL if n == "Rebolos" else AZUL_CLARO for n in nomes]
    ax.barh(nomes, vals, color=cores, height=0.6)
    for i, (n, vv) in enumerate(zip(nomes, vals)):
        ax.text(vv + 0.06, i, f"{num(vv,1)} kg · {num(vv/kg*100,1)}%", va="center", fontsize=10, color=TINTA)
    ax.set_xlim(0, 4.4)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0, labelcolor=TINTA, labelsize=11)
    ax.xaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(lambda x, _: num(x, 1))
    ax.set_xlabel("kg na amostra de 10 m²", fontsize=10)
    fig.text(0.04, 0.44, "Composição da perda", fontsize=12, fontweight="bold", color=TINTA)
    fig.text(0.04, 0.415, "Causa principal: rebolos → verificar picador, extrator e sincronia do transbordo",
             fontsize=9.5, color=TINTA_2)

    # --- prejuízo atual x meta ---
    ax = fig.add_axes([0.58, 0.07, 0.38, 0.33])
    barras = ["Prejuízo atual\n(7,81%)", "Prejuízo na meta\n(5%)"]
    ax.bar(barras, [prejuizo, prejuizo_meta], color=[AZUL, CINZA], width=0.5)
    ax.text(0, prejuizo + 2500, brl(prejuizo, 0), ha="center", fontsize=11, fontweight="bold", color=TINTA)
    ax.text(1, prejuizo_meta + 2500, brl(prejuizo_meta, 0), ha="center", fontsize=11, fontweight="bold", color=TINTA)
    ax.annotate("", xy=(1, prejuizo), xytext=(1, prejuizo_meta + 9000),
                arrowprops=dict(arrowstyle="<->", color=BOM, lw=1.8))
    ax.plot([0.25, 1], [prejuizo, prejuizo], color=MUDO, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.text(1.28, (prejuizo + prejuizo_meta + 9000) / 2, f"recuperável\n{brl(recuperavel, 0)}",
            fontsize=10.5, fontweight="bold", color="#006300", va="center")
    ax.set_ylim(0, 125000); ax.set_xlim(-0.5, 1.9)
    ax.yaxis.set_major_formatter(lambda x, _: f"{x/1000:.0f} mil")
    ax.tick_params(axis="x", labelcolor=TINTA, length=0)
    grade_y(ax)
    fig.text(0.53, 0.44, "Quanto volta para o caixa na meta", fontsize=12, fontweight="bold", color=TINTA)
    fig.text(0.53, 0.415, "Reduzir a perda de 7,81% para 5% no talhão de 100 ha", fontsize=9.5, color=TINTA_2)

    fig.text(0.04, -0.03, "Fonte: roteiro de demonstração do ColheitaCerta; preço AFCP-PE (estimativa set/2026); "
             "referência de perdas IAC.", fontsize=8.5, color=MUDO)
    salvar(fig, "01_dashboard.png")


# =====================================================================
# 2) FLUXO DO SISTEMA
# =====================================================================
def fluxo():
    fig, ax = plt.subplots(figsize=(13, 3.6))
    ax.set_axis_off(); ax.set_xlim(0, 13); ax.set_ylim(0, 3.6)
    etapas = [
        ("1. Amostra", "10 m² logo após\na colhedora"),
        ("2. Pesagem", "inteira · rebolos\ntocos · lascas"),
        ("3. Cálculo", "t/ha · % ·\ntoneladas · R$"),
        ("4. Classificação", "BAIXA · MÉDIA\nALTA"),
        ("5. Diagnóstico", "perda predominante\n→ regulagem"),
        ("6. Painel", "ranking de talhões\n+ valor recuperável"),
    ]
    bw, gap = 1.85, 0.27
    for i, (t, d) in enumerate(etapas):
        x = 0.15 + i * (bw + gap)
        cor = AZUL if i in (2, 4) else "white"
        ink = "white" if i in (2, 4) else TINTA
        ax.add_patch(FancyBboxPatch((x, 0.75), bw, 1.9, boxstyle="round,pad=0,rounding_size=0.15",
                                    facecolor=cor, edgecolor=AZUL, linewidth=1.5))
        ax.text(x + bw / 2, 2.2, t, ha="center", fontsize=12, fontweight="bold", color=ink)
        ax.text(x + bw / 2, 1.45, d, ha="center", va="center", fontsize=9.8,
                color="white" if i in (2, 4) else TINTA_2)
        if i < len(etapas) - 1:
            ax.annotate("", xy=(x + bw + gap - 0.02, 1.7), xytext=(x + bw + 0.02, 1.7),
                        arrowprops=dict(arrowstyle="-|>", color=MUDO, lw=1.5))
    ax.text(0.15, 3.25, "Como o ColheitaCerta transforma a amostra em decisão", fontsize=14,
            fontweight="bold", color=TINTA)
    ax.text(0.15, 0.3, "Funciona sem internet: registros ficam em JSON local (IDs L1, L2...) e são "
            "sincronizados com o Oracle quando houver conexão.", fontsize=9.8, color=TINTA_2)
    salvar(fig, "02_fluxo.png")


# =====================================================================
# 3) PREJUÍZO POR TIPO DE PERDA
# =====================================================================
def prejuizo_por_tipo():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    nomes = list(AMOSTRA)[::-1]
    vals = [AMOSTRA[n] / kg * prejuizo for n in nomes]
    ax.barh(nomes, vals, color=[AZUL if n == "Rebolos" else AZUL_CLARO for n in nomes], height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + 800, i, brl(v, 0), va="center", fontsize=11, color=TINTA, fontweight="bold")
    ax.set_xlim(0, 55000)
    ax.xaxis.set_major_formatter(lambda x, _: f"R$ {x/1000:.0f} mil")
    ax.xaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0, labelcolor=TINTA, labelsize=11)
    titulo(ax, "Prejuízo por tipo de perda",
           f"Talhão de 100 ha, total {brl(prejuizo)} · participação na amostra × prejuízo total")
    salvar(fig, "03_prejuizo_por_tipo.png")


# =====================================================================
# 4) EXEMPLO X REFERÊNCIAS
# =====================================================================
def referencias():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    rot = ["Colheita manual\n(ref. IAC)", "Meta do\nColheitaCerta", "Exemplo\nT-001", "Mecanizada,\nmáximo (IAC)"]
    vals = [5, 5, perda_pct * 100, 15]
    cores = [CINZA, CINZA, AZUL, CINZA]
    ax.bar(rot, vals, color=cores, width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, f"{num(v, 2 if i == 2 else 0)}%", ha="center", fontsize=12, fontweight="bold", color=TINTA)
    ax.set_ylim(0, 17); ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0f}%")
    ax.tick_params(axis="x", labelcolor=TINTA, length=0)
    grade_y(ax)
    titulo(ax, "Onde o talhão de exemplo está frente às referências",
           "Perda em % da produção · referências: IAC, via Canal Rural")
    salvar(fig, "04_referencias.png")


# =====================================================================
# 5) SENSIBILIDADE: PREJUÍZO X % DE PERDA NO TALHÃO
# =====================================================================
def sensibilidade():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    xs = [i / 10 for i in range(0, 201)]
    ys = [PROD_THA * (p / 100) / (1 - p / 100) * AREA_HA * PRECO for p in xs]
    ax.axvspan(0, 5, color=BOM, alpha=0.07); ax.axvspan(5, 10, color=ALERTA, alpha=0.10)
    ax.axvspan(10, 20, color=CRITICO, alpha=0.07)
    for a, r in [(2.5, "BAIXA"), (7.5, "MÉDIA"), (15, "ALTA")]:
        ax.text(a, 395000, r, ha="center", fontsize=10, color=TINTA_2, fontweight="bold")
    ax.plot(xs, ys, color=AZUL, linewidth=2.2)
    pts = [(5, "meta 5%"), (perda_pct * 100, "exemplo 7,81%"), (15, "15%")]
    for p, r in pts:
        y = PROD_THA * (p / 100) / (1 - p / 100) * AREA_HA * PRECO
        ax.plot(p, y, "o", markersize=8, color=AZUL, markeredgecolor=SUPERFICIE, markeredgewidth=2)
        ax.text(p - 0.3, y + 14000, f"{r}\n{brl(y, 0)}", ha="right", fontsize=9.5, color=TINTA)
    ax.set_xlim(0, 20); ax.set_ylim(0, 420000); ax.xaxis.set_major_locator(MultipleLocator(2.5))
    ax.xaxis.set_major_formatter(lambda x, _: f"{num(x, 1 if x % 1 else 0)}%")
    ax.yaxis.set_major_formatter(lambda x, _: f"R$ {x/1000:.0f} mil")
    ax.set_xlabel("Perda sobre a produção (%)")
    grade_y(ax)
    titulo(ax, "Quanto custa cada ponto de perda no talhão",
           "100 ha · 85 t/ha colhidas · R$ 144,18/t (AFCP-PE set/2026)")
    salvar(fig, "05_sensibilidade_talhao.png")


# =====================================================================
# 6) ESCALA BRASIL
# =====================================================================
def brasil():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    niveis = [1, 5, perda_pct * 100, 10, 15]
    rot = ["1%", "5%", "7,81%\n(exemplo)", "10%", "15%"]
    vals = [PRODUCAO_BR * (p / 100) / (1 - p / 100) * PRECO / 1000 for p in niveis]
    ax.bar(rot, vals, color=[AZUL if i == 2 else AZUL_CLARO for i in range(5)], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, f"R$ {num(v)} bi", ha="center", fontsize=11, fontweight="bold", color=TINTA)
    ax.set_ylim(0, 20); ax.yaxis.set_major_locator(MultipleLocator(4)); ax.yaxis.set_major_formatter(lambda x, _: f"R$ {x:.0f} bi")
    ax.tick_params(axis="x", labelcolor=TINTA, length=0)
    ax.set_xlabel("Nível de perda (mesma fórmula do sistema: perda ÷ (colhido + perda))")
    grade_y(ax)
    titulo(ax, "Valor da cana deixada no campo no Brasil, safra 2026/27",
           "705,2 milhões t colhidas (Conab, 20/08/2026) × R$ 144,18/t (AFCP-PE set/2026) · estimativa de escala")
    salvar(fig, "06_escala_brasil.png")


# =====================================================================
# 7) PREÇO X CUSTO
# =====================================================================
def preco_custo():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    rot = ["Preço ago/2026\n(AFCP-PE)", "Preço set/2026\n(estimativa AFCP-PE)", "Custo de produção\n(CNA/Senar/Cepea)"]
    vals = [PRECO_AGO, PRECO, CUSTO]
    ax.bar(rot, vals, color=[AZUL_CLARO, AZUL, CINZA], width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 4, brl(v), ha="center", fontsize=12, fontweight="bold", color=TINTA)
    ax.set_ylim(0, 250); ax.yaxis.set_major_formatter(lambda x, _: f"R$ {x:.0f}")
    ax.tick_params(axis="x", labelcolor=TINTA, length=0)
    grade_y(ax)
    titulo(ax, "Por que cada tonelada perdida pesa: preço x custo (R$/t)",
           "Pernambuco · custo calculado sobre a safra 2025/26 · fonte: Movimento Econômico, 03/09/2026")
    salvar(fig, "07_preco_x_custo.png")


if __name__ == "__main__":
    dashboard(); fluxo(); prejuizo_por_tipo(); referencias(); sensibilidade(); brasil(); preco_custo()
