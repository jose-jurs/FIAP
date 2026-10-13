"""
arquivos.py
Manipulação de arquivos texto e JSON:
  - config/config.json ........ parâmetros do sistema (preço, meta, DSN)
  - data/base_local.json ...... espelho local dos dados (modo offline)
  - data/log_operacoes.txt .... histórico de operações (texto, modo append)
  - data/relatorio_*.txt ...... relatório gerencial exportado
  - data/resumo_*.json ........ resumo para integração com outros sistemas
"""
import json
from datetime import datetime
from pathlib import Path

# Raiz do projeto = pasta acima de src/
PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_CONFIG = PASTA_RAIZ / "config"
PASTA_DADOS = PASTA_RAIZ / "data"

ARQ_CONFIG = PASTA_CONFIG / "config.json"
ARQ_BASE_LOCAL = PASTA_DADOS / "base_local.json"
ARQ_LOG = PASTA_DADOS / "log_operacoes.txt"

CONFIG_PADRAO = {
    "preco_tonelada": 144.18,       # R$/t de cana (ref. AFCP-PE set/2026; ajuste pelo Consecana vigente)
    "meta_perda_pct": 5.0,          # meta de perda aceitável (%)
    "area_amostra_padrao_m2": 10.0,  # área padrão de cada amostragem
    "dsn": "oracle.fiap.com.br:1521/ORCL",
}


def garantir_pastas():
    """Procedimento: cria as pastas de configuração e dados se não existirem."""
    PASTA_CONFIG.mkdir(exist_ok=True)
    PASTA_DADOS.mkdir(exist_ok=True)


def ler_json(caminho, padrao):
    """
    Lê um arquivo JSON. Se não existir ou estiver corrompido, devolve o
    valor padrão (e guarda uma cópia do arquivo corrompido para análise).
    """
    if not caminho.exists():
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        copia = caminho.with_suffix(".corrompido.json")
        try:
            caminho.replace(copia)
        except OSError:
            pass
        print(f"   [!] {caminho.name} estava corrompido. Cópia salva em {copia.name}.")
        return padrao


def gravar_json(caminho, dados):
    """Grava o dicionário/lista em JSON legível (UTF-8, indentado)."""
    garantir_pastas()
    temporario = caminho.with_suffix(".tmp")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    temporario.replace(caminho)  # troca atômica: evita arquivo pela metade


def carregar_config():
    """Lê a configuração e completa chaves ausentes com os valores padrão."""
    config = dict(CONFIG_PADRAO)
    lida = ler_json(ARQ_CONFIG, {})
    if isinstance(lida, dict):
        for chave, valor in lida.items():
            if chave in CONFIG_PADRAO:
                config[chave] = valor
    if not ARQ_CONFIG.exists():
        gravar_json(ARQ_CONFIG, config)
    return config


def salvar_config(config):
    gravar_json(ARQ_CONFIG, config)


def carregar_base_local():
    """Retorna a tupla (talhoes, colheitas) salva localmente."""
    base = ler_json(ARQ_BASE_LOCAL, {"talhoes": {}, "colheitas": []})
    talhoes = base.get("talhoes", {}) if isinstance(base, dict) else {}
    colheitas = base.get("colheitas", []) if isinstance(base, dict) else []
    return talhoes, colheitas


def salvar_base_local(talhoes, colheitas):
    """Grava o espelho local com a data da última atualização."""
    gravar_json(ARQ_BASE_LOCAL, {
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
        "talhoes": talhoes,
        "colheitas": colheitas,
    })


def registrar_log(operacao, detalhe=""):
    """Procedimento: acrescenta uma linha no log de operações (arquivo texto)."""
    garantir_pastas()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQ_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{agora}] {operacao:<22} | {detalhe}\n")


def ler_ultimas_linhas_log(quantidade=15):
    """Lê o arquivo de log e devolve as últimas linhas."""
    if not ARQ_LOG.exists():
        return []
    with open(ARQ_LOG, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
    return [linha.rstrip("\n") for linha in linhas[-quantidade:]]


def exportar_relatorio_txt(linhas):
    """Grava o relatório gerencial em .txt e devolve o caminho gerado."""
    garantir_pastas()
    nome = f"relatorio_{datetime.now():%Y%m%d_%H%M%S}.txt"
    caminho = PASTA_DADOS / nome
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")
    return caminho


def exportar_resumo_json(resumo):
    """Grava o resumo gerencial em JSON e devolve o caminho gerado."""
    nome = f"resumo_{datetime.now():%Y%m%d_%H%M%S}.json"
    caminho = PASTA_DADOS / nome
    gravar_json(caminho, resumo)
    return caminho
