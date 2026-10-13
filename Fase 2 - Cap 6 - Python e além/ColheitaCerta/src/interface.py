"""
interface.py
Procedimentos de exibição no terminal: cabeçalhos, tabelas, barras e
formatação de números no padrão brasileiro.
"""
import os
from datetime import date

LARGURA = 96


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\n   Pressione ENTER para continuar...")


def linha(caractere="-"):
    print(caractere * LARGURA)


def cabecalho(titulo, subtitulo=""):
    linha("=")
    print(f" {titulo}".center(LARGURA))
    if subtitulo:
        print(f" {subtitulo}".center(LARGURA))
    linha("=")


def sucesso(mensagem):
    print(f"   [OK] {mensagem}")


def aviso(mensagem):
    print(f"   [!] {mensagem}")


def numero_br(valor, casas=2):
    """1234567.891 -> '1.234.567,89'"""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def moeda(valor):
    return f"R$ {numero_br(valor)}"


def data_br(data_iso):
    """'2026-09-30' -> '30/09/2026'"""
    return date.fromisoformat(data_iso).strftime("%d/%m/%Y")


def formatar_tabela(colunas, linhas):
    """
    Função: recebe a lista de tuplas (título, largura, alinhamento) e as
    linhas de dados; devolve a lista de strings da tabela já formatada.
    """
    def montar(valores):
        partes = []
        for (_, largura, alinhamento), valor in zip(colunas, valores):
            texto = str(valor)
            if len(texto) > largura:
                texto = texto[:largura - 1] + "…"
            partes.append(f"{texto:{alinhamento}{largura}}")
        return " | ".join(partes)

    titulo = montar([c[0] for c in colunas])
    separador = "-+-".join("-" * c[1] for c in colunas)
    resultado = [titulo, separador]
    for valores in linhas:
        resultado.append(montar(valores))
    return resultado


def imprimir_tabela(colunas, linhas):
    """Procedimento: imprime a tabela formatada ou avisa se estiver vazia."""
    if not linhas:
        aviso("Nenhum registro encontrado.")
        return
    for texto in formatar_tabela(colunas, linhas):
        print("  " + texto)


def barra(valor, valor_maximo, largura=30):
    """Barra horizontal proporcional para gráficos no terminal."""
    if valor_maximo <= 0:
        return ""
    preenchido = round(valor / valor_maximo * largura)
    return "█" * preenchido + "░" * (largura - preenchido)
