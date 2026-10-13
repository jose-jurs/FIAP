"""
validacoes.py
Funções de leitura e consistência dos dados digitados pelo usuário.

Todas as funções repetem a pergunta até receber um valor válido,
garantindo que nenhum tipo indesejado chegue aos cálculos ou ao banco.
"""
import math
import re
from datetime import date, datetime

# Tupla com as respostas aceitas para perguntas de sim/não
RESPOSTAS_SIM = ("S", "SIM", "Y")
RESPOSTAS_NAO = ("N", "NAO", "NÃO")

# Código do talhão: 1 a 3 letras, hífen opcional e 1 a 4 números (ex.: T-001, AB12)
PADRAO_CODIGO_TALHAO = re.compile(r"^[A-Z]{1,3}-?\d{1,4}$")


def formatar_numero(valor):
    """Exibe números no padrão brasileiro nas mensagens (120.5 -> 120,5)."""
    return f"{valor:g}".replace(".", ",")


def mostrar_erro(mensagem):
    """Procedimento: exibe uma mensagem de erro padronizada."""
    print(f"   [!] {mensagem}")


def ler_texto(mensagem, tamanho_min=1, tamanho_max=60, obrigatorio=True):
    """Lê um texto respeitando tamanho mínimo e máximo."""
    while True:
        valor = input(mensagem).strip()
        if not valor and not obrigatorio:
            return ""
        if len(valor) < tamanho_min:
            mostrar_erro(f"Informe pelo menos {tamanho_min} caractere(s).")
        elif len(valor) > tamanho_max:
            mostrar_erro(f"Máximo de {tamanho_max} caracteres.")
        else:
            return valor


def ler_float(mensagem, minimo=None, maximo=None, obrigatorio=True, padrao=None):
    """Lê um número decimal. Aceita vírgula ou ponto como separador."""
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        if not bruto:
            if padrao is not None:
                return padrao
            if not obrigatorio:
                return None
            mostrar_erro("Campo obrigatório.")
            continue
        try:
            valor = float(bruto)
        except ValueError:
            mostrar_erro("Digite um número válido (ex.: 12,5).")
            continue
        if not math.isfinite(valor):
            mostrar_erro("Digite um número finito.")
        elif minimo is not None and valor < minimo:
            mostrar_erro(f"O valor mínimo é {formatar_numero(minimo)}.")
        elif maximo is not None and valor > maximo:
            mostrar_erro(f"O valor máximo é {formatar_numero(maximo)}.")
        else:
            return round(valor, 3)


def ler_inteiro(mensagem, minimo=None, maximo=None):
    """Lê um número inteiro dentro de um intervalo opcional."""
    while True:
        bruto = input(mensagem).strip()
        try:
            valor = int(bruto)
        except ValueError:
            mostrar_erro("Digite um número inteiro.")
            continue
        if minimo is not None and valor < minimo:
            mostrar_erro(f"O valor mínimo é {formatar_numero(minimo)}.")
        elif maximo is not None and valor > maximo:
            mostrar_erro(f"O valor máximo é {formatar_numero(maximo)}.")
        else:
            return valor


def ler_opcao(mensagem, opcoes_validas):
    """Lê uma opção e garante que ela pertence à tupla/lista de opções válidas."""
    opcoes = tuple(str(o).upper() for o in opcoes_validas)
    while True:
        valor = input(mensagem).strip().upper()
        if valor in opcoes:
            return valor
        mostrar_erro(f"Opção inválida. Escolha entre: {', '.join(opcoes)}.")


def ler_sim_nao(mensagem):
    """Retorna True para sim e False para não."""
    while True:
        valor = input(mensagem).strip().upper()
        if valor in RESPOSTAS_SIM:
            return True
        if valor in RESPOSTAS_NAO:
            return False
        mostrar_erro("Responda S (sim) ou N (não).")


def ler_data(mensagem, permitir_hoje_vazio=True):
    """
    Lê uma data no formato dd/mm/aaaa.
    Não aceita datas futuras nem anteriores a 2000.
    Retorna a data no formato ISO (aaaa-mm-dd) para facilitar o JSON.
    """
    while True:
        bruto = input(mensagem).strip()
        if not bruto and permitir_hoje_vazio:
            return date.today().isoformat()
        try:
            data_lida = datetime.strptime(bruto, "%d/%m/%Y").date()
        except ValueError:
            mostrar_erro("Data inválida. Use o formato dd/mm/aaaa.")
            continue
        if data_lida > date.today():
            mostrar_erro("A data não pode estar no futuro.")
        elif data_lida.year < 2000:
            mostrar_erro("Informe uma data a partir de 2000.")
        else:
            return data_lida.isoformat()


def validar_codigo_talhao(codigo):
    """Função: retorna True se o código segue o padrão definido."""
    return bool(PADRAO_CODIGO_TALHAO.match(codigo))


def ler_codigo_talhao(mensagem):
    """Lê o código de um talhão, convertendo para maiúsculas."""
    while True:
        codigo = input(mensagem).strip().upper()
        if validar_codigo_talhao(codigo):
            return codigo
        mostrar_erro("Código inválido. Use letras + números, ex.: T-001, AB12.")
