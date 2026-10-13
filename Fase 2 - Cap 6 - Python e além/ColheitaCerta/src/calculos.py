"""
calculos.py
Regras de negócio: cálculo das perdas na colheita de cana-de-açúcar,
classificação, diagnóstico da causa provável e indicadores gerenciais.

Metodologia (amostragem de campo):
  - Numa área de amostra (ex.: 10 m²) recolhe-se e pesa-se a cana que
    ficou no chão, separada por tipo de perda.
  - 1 kg/m² equivale a 10 t/ha  ->  perda (t/ha) = kg / m² * 10
  - Perda % = perda / (produtividade colhida + perda) * 100
"""

# ---------------------------------------------------------------------------
# Estruturas de apoio (tuplas e dicionários constantes)
# ---------------------------------------------------------------------------

# Tupla com os tipos de perda medidos na amostragem (ordem fixa)
TIPOS_PERDA = ("cana_inteira", "rebolos", "tocos", "lascas")

NOMES_PERDA = {
    "cana_inteira": "Cana inteira",
    "rebolos": "Rebolos (pedaços)",
    "tocos": "Tocos",
    "lascas": "Lascas/estilhaços",
}

# Dicionário: causa provável + recomendação para cada tipo de perda
RECOMENDACOES = {
    "cana_inteira": (
        "Colmos não recolhidos pela colhedora (cana acamada ou desalinhamento).",
        "Ajustar divisores de linha e despontador; usar piloto automático/RTK "
        "para manter a colhedora alinhada; reduzir velocidade em cana acamada.",
    ),
    "rebolos": (
        "Rebolos lançados junto com a palha pelo extrator ou fora do transbordo.",
        "Reduzir a rotação do extrator primário, controlar a velocidade de "
        "deslocamento e sincronizar colhedora e transbordo.",
    ),
    "tocos": (
        "Corte de base alto, deixando parte do colmo no campo.",
        "Regular a altura do corte de base (controle automático de altura), "
        "verificar facas do disco e a sistematização do terreno.",
    ),
    "lascas": (
        "Colmos estilhaçados por facas do picador gastas ou mal reguladas.",
        "Trocar/afiar as facas do picador e revisar os rolos alimentadores.",
    ),
}

TIPOS_COLHEITA = {"MEC": "Mecânica", "MAN": "Manual"}

# Tupla de tuplas: (limite superior %, nível, descrição)
FAIXAS_PERDA = (
    (5.0, "BAIXA", "Dentro da referência da colheita manual (até 5%)."),
    (10.0, "MÉDIA", "Acima do ideal. Revisar a regulagem da operação."),
    (float("inf"), "ALTA", "Perda crítica. Intervenção imediata recomendada."),
)


# ---------------------------------------------------------------------------
# Funções de cálculo
# ---------------------------------------------------------------------------

def total_kg_amostra(perdas_kg):
    """Soma os quilos de todos os tipos de perda da amostra."""
    return sum(perdas_kg.get(tipo, 0.0) for tipo in TIPOS_PERDA)


def calcular_perda_t_ha(perdas_kg, area_amostra_m2):
    """Converte o peso recolhido na amostra em toneladas por hectare."""
    if area_amostra_m2 <= 0:
        return 0.0
    return total_kg_amostra(perdas_kg) / area_amostra_m2 * 10


def calcular_perda_percentual(perda_t_ha, produtividade_t_ha):
    """Percentual da cana produzida que ficou no campo."""
    producao_total = produtividade_t_ha + perda_t_ha
    if producao_total <= 0:
        return 0.0
    return perda_t_ha / producao_total * 100


def classificar_perda(percentual):
    """Retorna a tupla (nível, descrição) conforme as faixas definidas."""
    for limite, nivel, descricao in FAIXAS_PERDA:
        if percentual <= limite:
            return nivel, descricao
    return FAIXAS_PERDA[-1][1], FAIXAS_PERDA[-1][2]


def diagnosticar(perdas_kg):
    """
    Monta a lista de participação de cada tipo de perda, ordenada da maior
    para a menor. Cada item é uma tupla (tipo, kg, participação %).
    """
    total = total_kg_amostra(perdas_kg)
    participacoes = []
    for tipo in TIPOS_PERDA:
        kg = perdas_kg.get(tipo, 0.0)
        pct = kg / total * 100 if total > 0 else 0.0
        participacoes.append((tipo, kg, pct))
    participacoes.sort(key=lambda item: item[1], reverse=True)
    return participacoes


def perda_na_meta_t_ha(produtividade_t_ha, meta_pct):
    """Perda máxima (t/ha) que ainda atende à meta percentual."""
    m = meta_pct / 100
    if m >= 1:
        return float("inf")
    return m * produtividade_t_ha / (1 - m)


def enriquecer_colheita(colheita, config):
    """
    Recebe o registro bruto (dicionário) e devolve um NOVO dicionário com
    todos os indicadores calculados, usando o preço e a meta da configuração.
    """
    preco = config["preco_tonelada"]
    meta = config["meta_perda_pct"]

    perda_tha = calcular_perda_t_ha(colheita["perdas_kg"], colheita["area_amostra_m2"])
    perda_pct = calcular_perda_percentual(perda_tha, colheita["produtividade_t_ha"])
    nivel, descricao = classificar_perda(perda_pct)
    toneladas_perdidas = perda_tha * colheita["area_colhida_ha"]

    excesso_tha = max(0.0, perda_tha - perda_na_meta_t_ha(colheita["produtividade_t_ha"], meta))
    ganho_potencial = excesso_tha * colheita["area_colhida_ha"] * preco

    resultado = dict(colheita)
    resultado.update({
        "perda_t_ha": perda_tha,
        "perda_pct": perda_pct,
        "nivel": nivel,
        "descricao_nivel": descricao,
        "toneladas_perdidas": toneladas_perdidas,
        "prejuizo": toneladas_perdidas * preco,
        "ganho_potencial": ganho_potencial,
        "diagnostico": diagnosticar(colheita["perdas_kg"]),
    })
    return resultado


def resumo_por_tipo_colheita(colheitas_enriquecidas):
    """
    Compara colheita manual x mecânica.
    Retorna dicionário: tipo -> {qtd, area, perda_media_pct, toneladas, prejuizo}
    A perda média é ponderada pela área colhida.
    """
    resumo = {}
    for tipo in TIPOS_COLHEITA:
        registros = [c for c in colheitas_enriquecidas if c["tipo"] == tipo]
        area = sum(c["area_colhida_ha"] for c in registros)
        media = (sum(c["perda_pct"] * c["area_colhida_ha"] for c in registros) / area
                 if area > 0 else 0.0)
        resumo[tipo] = {
            "qtd": len(registros),
            "area": area,
            "perda_media_pct": media,
            "toneladas": sum(c["toneladas_perdidas"] for c in registros),
            "prejuizo": sum(c["prejuizo"] for c in registros),
        }
    return resumo


def ranking_talhoes(colheitas_enriquecidas):
    """
    Lista de tuplas (código do talhão, perda média %, prejuízo total),
    ordenada do talhão mais crítico para o menos crítico.
    """
    agrupado = {}
    for c in colheitas_enriquecidas:
        dados = agrupado.setdefault(c["codigo_talhao"], [0.0, 0.0, 0.0])
        dados[0] += c["perda_pct"] * c["area_colhida_ha"]
        dados[1] += c["area_colhida_ha"]
        dados[2] += c["prejuizo"]

    ranking = []
    for codigo, (soma_pond, area, prejuizo) in agrupado.items():
        media = soma_pond / area if area > 0 else 0.0
        ranking.append((codigo, media, prejuizo))
    ranking.sort(key=lambda item: item[1], reverse=True)
    return ranking


def causa_predominante_geral(colheitas_enriquecidas):
    """Soma os kg de cada tipo em todas as amostras e retorna o tipo dominante."""
    totais = {tipo: 0.0 for tipo in TIPOS_PERDA}
    for c in colheitas_enriquecidas:
        for tipo in TIPOS_PERDA:
            totais[tipo] += c["perdas_kg"].get(tipo, 0.0)
    if sum(totais.values()) == 0:
        return None
    return max(totais, key=totais.get)
