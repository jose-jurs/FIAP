# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Aplicacao de apoio a Agricultura Digital
=============================================================

Culturas suportadas (principais do estado de Sao Paulo):
    1) Cafe          -> area calculada como RETANGULO
    2) Cana-de-acucar -> area calculada como TRAPEZIO

O programa mantem os dados organizados em VETORES (listas paralelas),
oferece um MENU de opcoes (entrada, saida, atualizacao, delecao e sair)
e usa rotinas de LOOP e DECISAO em toda a navegacao.

Ao final, os registros podem ser exportados para 'dados.csv', que e lido
pela aplicacao em R para o calculo das estatisticas (media e desvio padrao).

Autor: Grupo FarmTech Solutions
"""

# ---------------------------------------------------------------------------
# VETORES DE DADOS (listas paralelas)
# Cada indice 'i' representa UM registro de plantio.
# ---------------------------------------------------------------------------
culturas = []        # str  -> "Cafe" ou "Cana-de-acucar"
areas = []           # float-> area de plantio em metros quadrados (m2)
produtos = []        # str  -> insumo aplicado (ex.: "Fosfato")
litros_insumo = []   # float-> total de insumo necessario em litros (L)

# Constantes de conversao
M2_POR_HECTARE = 10000.0


# ===========================================================================
# FUNCOES AUXILIARES DE ENTRADA (validacao)
# ===========================================================================
def ler_float(mensagem):
    """Le um numero decimal positivo do teclado, repetindo ate ser valido."""
    while True:
        entrada = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(entrada)
            if valor <= 0:
                print("  >> Digite um valor maior que zero.")
                continue
            return valor
        except ValueError:
            print("  >> Valor invalido. Use apenas numeros (ex.: 12.5).")


def ler_int(mensagem):
    """Le um numero inteiro positivo do teclado, repetindo ate ser valido."""
    while True:
        entrada = input(mensagem).strip()
        try:
            valor = int(entrada)
            if valor <= 0:
                print("  >> Digite um inteiro maior que zero.")
                continue
            return valor
        except ValueError:
            print("  >> Valor invalido. Use apenas numeros inteiros.")


# ===========================================================================
# CALCULO DE AREA (figura geometrica por cultura)
# ===========================================================================
def calcular_area_cafe():
    """Cafe: talhao RETANGULAR. Area = comprimento x largura."""
    print("\n-- Area do talhao de CAFE (retangulo) --")
    comprimento = ler_float("  Comprimento do talhao (m): ")
    largura = ler_float("  Largura do talhao (m): ")
    area = comprimento * largura
    print(f"  Area calculada: {area:.2f} m2 ({area / M2_POR_HECTARE:.4f} ha)")
    return area


def calcular_area_cana():
    """Cana: talhao TRAPEZOIDAL (terrenos irregulares).
    Area = ((base_maior + base_menor) / 2) x altura."""
    print("\n-- Area do talhao de CANA-DE-ACUCAR (trapezio) --")
    base_maior = ler_float("  Base maior do talhao (m): ")
    base_menor = ler_float("  Base menor do talhao (m): ")
    altura = ler_float("  Altura (distancia entre as bases) (m): ")
    area = ((base_maior + base_menor) / 2.0) * altura
    print(f"  Area calculada: {area:.2f} m2 ({area / M2_POR_HECTARE:.4f} ha)")
    return area


# ===========================================================================
# CALCULO DO MANEJO DE INSUMOS
# ===========================================================================
def calcular_insumo_cafe():
    """Manejo por RUAS da lavoura de cafe.
    Exemplo do enunciado: aplicar fosfato pulverizando 500 mL por metro de rua.
    Total (L) = (dose_mL_por_metro x comprimento_rua x numero_de_ruas) / 1000.
    """
    print("\n-- Manejo de insumo - CAFE (por ruas) --")
    produto = input("  Produto/insumo (ex.: Fosfato): ").strip() or "Fosfato"
    dose_ml_m = ler_float("  Dose de aplicacao (mL por metro de rua): ")
    comprimento_rua = ler_float("  Comprimento de cada rua (m): ")
    n_ruas = ler_int("  Quantas ruas tem a lavoura? ")

    total_ml = dose_ml_m * comprimento_rua * n_ruas
    total_l = total_ml / 1000.0
    print(f"  Metros lineares totais: {comprimento_rua * n_ruas:.1f} m")
    print(f"  Insumo necessario: {total_l:.2f} L de {produto}")
    return produto, total_l


def calcular_insumo_cana():
    """Manejo por AREA (hectare) da lavoura de cana.
    Total (L) = dose_L_por_hectare x area_em_hectares.
    """
    print("\n-- Manejo de insumo - CANA (por hectare) --")
    produto = input("  Produto/insumo (ex.: Herbicida): ").strip() or "Herbicida"
    dose_l_ha = ler_float("  Dose de aplicacao (L por hectare): ")
    area_ha = ler_float("  Area a tratar (ha): ")

    total_l = dose_l_ha * area_ha
    print(f"  Insumo necessario: {total_l:.2f} L de {produto}")
    return produto, total_l


# ===========================================================================
# OPCOES DO MENU
# ===========================================================================
def entrada_de_dados():
    """Opcao 1: cadastra um novo registro de plantio nos vetores."""
    print("\n===== ENTRADA DE DADOS =====")
    print("Escolha a cultura:")
    print("  1 - Cafe (area retangular)")
    print("  2 - Cana-de-acucar (area trapezoidal)")
    opcao = input("Opcao: ").strip()

    if opcao == "1":
        cultura = "Cafe"
        area = calcular_area_cafe()
        produto, litros = calcular_insumo_cafe()
    elif opcao == "2":
        cultura = "Cana-de-acucar"
        area = calcular_area_cana()
        produto, litros = calcular_insumo_cana()
    else:
        print("  >> Cultura invalida. Registro cancelado.")
        return

    # Grava nos vetores (mesmo indice em todas as listas)
    culturas.append(cultura)
    areas.append(area)
    produtos.append(produto)
    litros_insumo.append(litros)
    print(f"\n  [OK] Registro #{len(culturas)} cadastrado com sucesso.")


def saida_de_dados():
    """Opcao 2: imprime no terminal todos os registros cadastrados."""
    print("\n===== SAIDA DE DADOS (registros cadastrados) =====")
    if not culturas:
        print("  Nenhum registro cadastrado ainda.")
        return

    print(f"{'#':<3} {'Cultura':<16} {'Area (m2)':>12} "
          f"{'Insumo':<14} {'Litros (L)':>12}")
    print("-" * 60)
    for i in range(len(culturas)):
        # Exibe numeracao 1-based (mais natural para o usuario)
        print(f"{i + 1:<3} {culturas[i]:<16} {areas[i]:>12.2f} "
              f"{produtos[i]:<14} {litros_insumo[i]:>12.2f}")
    print("-" * 60)
    print(f"  Total de registros: {len(culturas)}")
    print(f"  Area total plantada: {sum(areas):.2f} m2")
    print(f"  Insumo total: {sum(litros_insumo):.2f} L")


def atualizar_dado():
    """Opcao 3: atualiza um registro em uma posicao qualquer do vetor."""
    print("\n===== ATUALIZACAO DE DADOS =====")
    if not culturas:
        print("  Nenhum registro para atualizar.")
        return

    saida_de_dados()
    numero = ler_int("\n  Informe o numero (#) do registro a atualizar: ")
    indice = numero - 1  # converte de 1-based (usuario) para 0-based (lista)
    if indice < 0 or indice >= len(culturas):
        print("  >> Numero fora do intervalo.")
        return

    print(f"\n  Reescrevendo o registro #{numero} "
          f"({culturas[indice]}). Digite os novos dados:")
    print("  Escolha a cultura:")
    print("    1 - Cafe (retangulo)")
    print("    2 - Cana-de-acucar (trapezio)")
    opcao = input("  Opcao: ").strip()

    if opcao == "1":
        culturas[indice] = "Cafe"
        areas[indice] = calcular_area_cafe()
        produtos[indice], litros_insumo[indice] = calcular_insumo_cafe()
    elif opcao == "2":
        culturas[indice] = "Cana-de-acucar"
        areas[indice] = calcular_area_cana()
        produtos[indice], litros_insumo[indice] = calcular_insumo_cana()
    else:
        print("  >> Cultura invalida. Atualizacao cancelada.")
        return

    print(f"\n  [OK] Registro #{numero} atualizado.")


def deletar_dado():
    """Opcao 4: remove um registro de uma posicao qualquer do vetor."""
    print("\n===== DELECAO DE DADOS =====")
    if not culturas:
        print("  Nenhum registro para deletar.")
        return

    saida_de_dados()
    numero = ler_int("\n  Informe o numero (#) do registro a deletar: ")
    indice = numero - 1  # converte de 1-based (usuario) para 0-based (lista)
    if indice < 0 or indice >= len(culturas):
        print("  >> Numero fora do intervalo.")
        return

    removido = culturas[indice]
    # Remove o mesmo indice em TODOS os vetores (mantem paralelismo)
    culturas.pop(indice)
    areas.pop(indice)
    produtos.pop(indice)
    litros_insumo.pop(indice)
    print(f"\n  [OK] Registro #{numero} ({removido}) removido.")


def exportar_csv():
    """Opcao 5: grava os vetores em dados.csv (consumido pela app em R)."""
    print("\n===== EXPORTAR PARA CSV =====")
    if not culturas:
        print("  Nenhum registro para exportar.")
        return

    with open("dados.csv", "w", encoding="utf-8") as arquivo:
        arquivo.write("cultura,area_m2,produto,litros\n")
        for i in range(len(culturas)):
            arquivo.write(f"{culturas[i]},{areas[i]:.2f},"
                          f"{produtos[i]},{litros_insumo[i]:.2f}\n")
    print(f"  [OK] {len(culturas)} registros exportados para 'dados.csv'.")


# ===========================================================================
# MENU PRINCIPAL (loop + decisao)
# ===========================================================================
def carregar_exemplos():
    """Popula alguns registros de exemplo para facilitar a demonstracao."""
    culturas.extend(["Cafe", "Cana-de-acucar", "Cafe"])
    areas.extend([20000.0, 35000.0, 15000.0])
    produtos.extend(["Fosfato", "Herbicida", "Fosfato"])
    litros_insumo.extend([250.0, 105.0, 180.0])


def menu():
    print("=" * 60)
    print("       FARMTECH SOLUTIONS - AGRICULTURA DIGITAL")
    print("=" * 60)

    # Pergunta se deseja carregar dados de exemplo (facilita o video)
    if input("Carregar dados de exemplo? (s/n): ").strip().lower() == "s":
        carregar_exemplos()
        print("  [OK] 3 registros de exemplo carregados.")

    while True:  # LOOP principal do menu
        print("\n" + "-" * 60)
        print("MENU DE OPCOES")
        print("  1 - Entrada de dados")
        print("  2 - Saida de dados (imprimir)")
        print("  3 - Atualizar dado (posicao do vetor)")
        print("  4 - Deletar dado (posicao do vetor)")
        print("  5 - Exportar para CSV (para a app em R)")
        print("  6 - Sair do programa")
        print("-" * 60)

        opcao = input("Escolha uma opcao: ").strip()

        # Estrutura de DECISAO
        if opcao == "1":
            entrada_de_dados()
        elif opcao == "2":
            saida_de_dados()
        elif opcao == "3":
            atualizar_dado()
        elif opcao == "4":
            deletar_dado()
        elif opcao == "5":
            exportar_csv()
        elif opcao == "6":
            print("\nEncerrando o programa. Ate mais!")
            break
        else:
            print("  >> Opcao invalida. Escolha um numero de 1 a 6.")


if __name__ == "__main__":
    menu()
