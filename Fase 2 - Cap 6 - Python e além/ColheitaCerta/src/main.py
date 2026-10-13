"""
ColheitaCerta - Monitor de Perdas na Colheita de Cana-de-Açúcar
Programa principal: menu, fluxo das operações e integração dos módulos.

Execução:  python src/main.py
"""
import os
import sys
import textwrap
from datetime import datetime
from getpass import getpass

import arquivos
import calculos
import interface as ui
import validacoes as v

try:
    import oracledb
    import banco
    ORACLE_DISPONIVEL = True
except ImportError:  # biblioteca não instalada: o sistema segue em modo offline
    ORACLE_DISPONIVEL = False

# Tupla com as opções do menu: (código, descrição, seção)
OPCOES_MENU = (
    ("1", "Cadastrar talhão", "TALHÕES"),
    ("2", "Listar talhões", "TALHÕES"),
    ("3", "Editar talhão", "TALHÕES"),
    ("4", "Excluir talhão", "TALHÕES"),
    ("5", "Registrar amostragem de perdas", "COLHEITAS"),
    ("6", "Listar colheitas", "COLHEITAS"),
    ("7", "Diagnóstico de uma colheita", "COLHEITAS"),
    ("8", "Excluir colheita", "COLHEITAS"),
    ("9", "Painel gerencial", "ANÁLISES"),
    ("10", "Exportar relatório (TXT + JSON)", "ANÁLISES"),
    ("11", "Configurações", "SISTEMA"),
    ("12", "Conectar / sincronizar com o Oracle", "SISTEMA"),
    ("13", "Ver log de operações", "SISTEMA"),
    ("0", "Sair", "SISTEMA"),
)


# ===========================================================================
# Utilidades de estado
# ===========================================================================

def online(estado):
    return estado["conexao"] is not None


def persistir(estado):
    """Procedimento: grava o espelho local em JSON após qualquer alteração."""
    arquivos.salvar_base_local(estado["talhoes"], estado["colheitas"])


def rotulo_id(colheita):
    """Registros ainda não enviados ao banco aparecem como L1, L2..."""
    return f"L{-colheita['id']}" if colheita["pendente"] else str(colheita["id"])


def proximo_id_local(colheitas):
    menores = [c["id"] for c in colheitas if c["pendente"]]
    return min(menores, default=0) - 1


def buscar_colheita(estado, rotulo):
    for colheita in estado["colheitas"]:
        if rotulo_id(colheita) == rotulo.upper():
            return colheita
    return None


def colheitas_enriquecidas(estado, lista=None):
    lista = estado["colheitas"] if lista is None else lista
    return [calculos.enriquecer_colheita(c, estado["config"]) for c in lista]


def pode_alterar(estado, pendente):
    """No modo offline só é possível alterar o que ainda não foi ao banco."""
    if online(estado) or pendente:
        return True
    ui.aviso("Sem conexão: só é possível alterar registros criados offline (pendentes).")
    return False


# ===========================================================================
# Conexão
# ===========================================================================

def obter_credenciais():
    """Usa variáveis de ambiente se existirem; senão pergunta ao usuário."""
    usuario = os.environ.get("ORACLE_USER")
    senha = os.environ.get("ORACLE_PASSWORD")
    if usuario and senha:
        print(f"   Usando credenciais das variáveis de ambiente (usuário {usuario}).")
        return usuario, senha
    usuario = v.ler_texto("   Usuário Oracle (ex.: RM123456): ", tamanho_max=30)
    senha = getpass("   Senha: ")
    return usuario, senha


def tentar_conectar(config):
    """Função: devolve a conexão aberta ou None (modo offline)."""
    if not ORACLE_DISPONIVEL:
        ui.aviso("Biblioteca 'oracledb' não instalada (pip install -r requirements.txt).")
        return None
    while True:
        usuario, senha = obter_credenciais()
        try:
            print("   Conectando...")
            conexao = banco.conectar(usuario, senha, config["dsn"])
            banco.criar_tabelas(conexao)
            ui.sucesso("Conectado ao Oracle.")
            arquivos.registrar_log("CONEXAO", f"usuário {usuario}")
            return conexao
        except oracledb.Error as erro:
            ui.aviso(f"Falha na conexão: {str(erro).splitlines()[0]}")
            os.environ.pop("ORACLE_PASSWORD", None)  # evita repetir credencial errada
            if not v.ler_sim_nao("   Tentar novamente? (S/N): "):
                ui.aviso("Seguindo em MODO OFFLINE. Os dados ficam salvos em data/base_local.json.")
                return None


def carregar_dados(estado):
    """
    Online: carrega do Oracle e agrega registros pendentes criados offline.
    Offline: carrega o espelho local em JSON.
    """
    talhoes_locais, colheitas_locais = arquivos.carregar_base_local()
    if not online(estado):
        estado["talhoes"], estado["colheitas"] = talhoes_locais, colheitas_locais
        return

    estado["talhoes"] = banco.carregar_talhoes(estado["conexao"])
    estado["colheitas"] = banco.carregar_colheitas(estado["conexao"])

    for codigo, talhao in talhoes_locais.items():
        if talhao.get("pendente") and codigo not in estado["talhoes"]:
            estado["talhoes"][codigo] = talhao
    estado["colheitas"].extend(c for c in colheitas_locais if c.get("pendente"))
    persistir(estado)


def sincronizar(estado):
    """Envia ao Oracle tudo que foi registrado em modo offline."""
    conexao = estado["conexao"]
    enviados_t = enviados_c = 0

    for codigo, talhao in estado["talhoes"].items():
        if talhao["pendente"]:
            try:
                banco.inserir_talhao(conexao, codigo, talhao)
            except oracledb.IntegrityError:
                pass  # já existe no banco: apenas marca como sincronizado
            talhao["pendente"] = False
            enviados_t += 1

    for colheita in estado["colheitas"]:
        if colheita["pendente"]:
            colheita["id"] = banco.inserir_colheita(conexao, colheita, estado["config"])
            colheita["pendente"] = False
            enviados_c += 1

    persistir(estado)
    arquivos.registrar_log("SINCRONIZACAO", f"{enviados_t} talhão(ões), {enviados_c} colheita(s)")
    ui.sucesso(f"Sincronizados: {enviados_t} talhão(ões) e {enviados_c} colheita(s).")


def quantidade_pendentes(estado):
    t = sum(1 for x in estado["talhoes"].values() if x["pendente"])
    c = sum(1 for x in estado["colheitas"] if x["pendente"])
    return t, c


# ===========================================================================
# Talhões
# ===========================================================================

def cadastrar_talhao(estado):
    ui.cabecalho("CADASTRAR TALHÃO")
    codigo = v.ler_codigo_talhao("   Código do talhão (ex.: T-001): ")
    if codigo in estado["talhoes"]:
        ui.aviso(f"O talhão {codigo} já está cadastrado.")
        return
    talhao = {
        "fazenda": v.ler_texto("   Fazenda: ", tamanho_min=2, tamanho_max=60),
        "area_ha": v.ler_float("   Área do talhão (ha): ", minimo=0.01, maximo=100000),
        "variedade": v.ler_texto("   Variedade da cana (opcional, ex.: RB867515): ",
                                 tamanho_max=30, obrigatorio=False).upper(),
        "pendente": True,
    }
    if online(estado):
        try:
            banco.inserir_talhao(estado["conexao"], codigo, talhao)
            talhao["pendente"] = False
        except oracledb.Error as erro:
            ui.aviso(f"Erro no banco ({str(erro).splitlines()[0]}). Salvo como pendente.")
    estado["talhoes"][codigo] = talhao
    persistir(estado)
    arquivos.registrar_log("CADASTRO_TALHAO", f"{codigo} - {talhao['fazenda']}")
    ui.sucesso(f"Talhão {codigo} cadastrado" + (" (pendente de sincronização)." if talhao["pendente"] else "."))


def listar_talhoes(estado, pausar=True):
    ui.cabecalho("TALHÕES CADASTRADOS")
    contagem = {}
    for c in estado["colheitas"]:
        contagem[c["codigo_talhao"]] = contagem.get(c["codigo_talhao"], 0) + 1

    colunas = [("Código", 8, "<"), ("Fazenda", 30, "<"), ("Área (ha)", 11, ">"),
               ("Variedade", 12, "<"), ("Colheitas", 9, ">"), ("Status", 9, "<")]
    linhas = [(cod, t["fazenda"], ui.numero_br(t["area_ha"]), t["variedade"] or "-",
               contagem.get(cod, 0), "pendente" if t["pendente"] else "ok")
              for cod, t in sorted(estado["talhoes"].items())]
    ui.imprimir_tabela(colunas, linhas)
    if linhas:
        area_total = sum(t["area_ha"] for t in estado["talhoes"].values())
        print(f"\n   Total: {len(linhas)} talhão(ões) | {ui.numero_br(area_total)} ha")
    if pausar:
        ui.pausar()


def escolher_talhao(estado):
    """Função: mostra os talhões e devolve um código existente (ou None)."""
    if not estado["talhoes"]:
        ui.aviso("Nenhum talhão cadastrado. Use a opção 1 primeiro.")
        return None
    listar_talhoes(estado, pausar=False)
    while True:
        codigo = v.ler_codigo_talhao("\n   Código do talhão: ")
        if codigo in estado["talhoes"]:
            return codigo
        ui.aviso("Talhão não encontrado.")


def editar_talhao(estado):
    codigo = escolher_talhao(estado)
    if codigo is None:
        return
    talhao = estado["talhoes"][codigo]
    if not pode_alterar(estado, talhao["pendente"]):
        return
    print("   (ENTER mantém o valor atual)")
    novo = dict(talhao)
    novo["fazenda"] = v.ler_texto(f"   Fazenda [{talhao['fazenda']}]: ", tamanho_min=2,
                                  obrigatorio=False) or talhao["fazenda"]
    novo["area_ha"] = v.ler_float(f"   Área (ha) [{ui.numero_br(talhao['area_ha'])}]: ",
                                  minimo=0.01, maximo=100000, padrao=talhao["area_ha"])
    novo["variedade"] = (v.ler_texto(f"   Variedade [{talhao['variedade'] or '-'}]: ",
                                     tamanho_max=30, obrigatorio=False).upper()
                         or talhao["variedade"])
    if online(estado) and not talhao["pendente"]:
        try:
            banco.atualizar_talhao(estado["conexao"], codigo, novo)
        except oracledb.Error as erro:
            ui.aviso(f"Erro no banco: {str(erro).splitlines()[0]}")
            return
    estado["talhoes"][codigo] = novo
    persistir(estado)
    arquivos.registrar_log("EDICAO_TALHAO", codigo)
    ui.sucesso(f"Talhão {codigo} atualizado.")


def excluir_talhao(estado):
    codigo = escolher_talhao(estado)
    if codigo is None:
        return
    if any(c["codigo_talhao"] == codigo for c in estado["colheitas"]):
        ui.aviso("Este talhão possui colheitas registradas. Exclua-as antes.")
        return
    talhao = estado["talhoes"][codigo]
    if not pode_alterar(estado, talhao["pendente"]):
        return
    if not v.ler_sim_nao(f"   Confirma a exclusão do talhão {codigo}? (S/N): "):
        return
    if online(estado) and not talhao["pendente"]:
        try:
            banco.excluir_talhao(estado["conexao"], codigo)
        except oracledb.Error as erro:
            ui.aviso(f"Erro no banco: {str(erro).splitlines()[0]}")
            return
    del estado["talhoes"][codigo]
    persistir(estado)
    arquivos.registrar_log("EXCLUSAO_TALHAO", codigo)
    ui.sucesso(f"Talhão {codigo} excluído.")


# ===========================================================================
# Colheitas
# ===========================================================================

def exibir_resultado(c, config):
    """Procedimento: mostra os indicadores e o diagnóstico de uma colheita."""
    print(f"\n   Talhão {c['codigo_talhao']} | {ui.data_br(c['data'])} | "
          f"Colheita {calculos.TIPOS_COLHEITA[c['tipo']].lower()} | "
          f"{ui.numero_br(c['area_colhida_ha'])} ha")
    ui.linha()
    print(f"   Perda estimada ........ {ui.numero_br(c['perda_t_ha'])} t/ha "
          f"({ui.numero_br(c['perda_pct'])}% da produção)")
    print(f"   Classificação ......... {c['nivel']} - {c['descricao_nivel']}")
    print(f"   Cana deixada no campo . {ui.numero_br(c['toneladas_perdidas'])} t")
    print(f"   Prejuízo estimado ..... {ui.moeda(c['prejuizo'])} "
          f"(a {ui.moeda(config['preco_tonelada'])}/t)")
    if c["ganho_potencial"] > 0:
        print(f"   Recuperável na meta ... {ui.moeda(c['ganho_potencial'])} "
              f"(se a perda cair para {ui.numero_br(config['meta_perda_pct'], 1)}%)")

    print("\n   Composição da perda na amostra:")
    for tipo, kg, pct in c["diagnostico"]:
        print(f"     {calculos.NOMES_PERDA[tipo]:<20} {ui.numero_br(kg, 3):>9} kg "
              f"{ui.barra(pct, 100, 25)} {ui.numero_br(pct, 1):>5}%")

    tipo_principal, kg_principal, _ = c["diagnostico"][0]
    if kg_principal > 0 and c["nivel"] != "BAIXA":
        causa, acao = calculos.RECOMENDACOES[tipo_principal]
        print()
        print(textwrap.fill(causa, 92, initial_indent="   Causa provável: ",
                            subsequent_indent=" " * 19))
        print(textwrap.fill(acao, 92, initial_indent="   Recomendação  : ",
                            subsequent_indent=" " * 19))
    elif c["nivel"] == "BAIXA":
        print("\n   Operação dentro da referência. Manter as regulagens atuais.")


def registrar_colheita(estado):
    ui.cabecalho("REGISTRAR AMOSTRAGEM DE PERDAS")
    codigo = escolher_talhao(estado)
    if codigo is None:
        return
    talhao = estado["talhoes"][codigo]
    config = estado["config"]

    print("\n   Dados da colheita")
    data = v.ler_data("   Data (dd/mm/aaaa, ENTER = hoje): ")
    tipo = v.ler_opcao("   Tipo de colheita - MEC (mecânica) ou MAN (manual): ",
                       tuple(calculos.TIPOS_COLHEITA))
    area_colhida = v.ler_float(f"   Área colhida (ha, até {ui.numero_br(talhao['area_ha'])}): ",
                               minimo=0.01, maximo=talhao["area_ha"])
    produtividade = v.ler_float("   Produtividade colhida (t/ha, entre 20 e 250): ",
                                minimo=20, maximo=250)

    print("\n   Amostragem de campo (cana recolhida do chão)")
    area_amostra = v.ler_float(
        f"   Área da amostra em m² (ENTER = {ui.numero_br(config['area_amostra_padrao_m2'], 1)}): ",
        minimo=1, maximo=1000, padrao=config["area_amostra_padrao_m2"])
    perdas = {}
    for tipo_perda in calculos.TIPOS_PERDA:
        perdas[tipo_perda] = v.ler_float(
            f"   kg de {calculos.NOMES_PERDA[tipo_perda].lower():<18} (ENTER = 0): ",
            minimo=0, maximo=500, padrao=0.0)

    colheita = {
        "id": 0,
        "codigo_talhao": codigo,
        "data": data,
        "tipo": tipo,
        "area_colhida_ha": area_colhida,
        "produtividade_t_ha": produtividade,
        "area_amostra_m2": area_amostra,
        "perdas_kg": perdas,
        "pendente": True,
    }
    resultado = calculos.enriquecer_colheita(colheita, config)
    exibir_resultado(resultado, config)

    if resultado["perda_pct"] > 40:
        ui.aviso("Perda acima de 40% é incomum. Confira os pesos e a área da amostra.")
    if not v.ler_sim_nao("\n   Salvar este registro? (S/N): "):
        ui.aviso("Registro descartado.")
        return

    if online(estado):
        try:
            colheita["id"] = banco.inserir_colheita(estado["conexao"], colheita, config)
            colheita["pendente"] = False
        except oracledb.Error as erro:
            ui.aviso(f"Erro no banco ({str(erro).splitlines()[0]}). Salvo como pendente.")
    if colheita["pendente"]:
        colheita["id"] = proximo_id_local(estado["colheitas"])

    estado["colheitas"].append(colheita)
    persistir(estado)
    arquivos.registrar_log("REGISTRO_COLHEITA",
                           f"{rotulo_id(colheita)} talhão {codigo} perda "
                           f"{resultado['perda_pct']:.2f}%")
    ui.sucesso(f"Colheita registrada com ID {rotulo_id(colheita)}.")


def filtrar_colheitas(estado):
    """Função: pergunta o filtro desejado e devolve a lista filtrada."""
    print("   Filtrar por: [T] todas  [A] talhão  [C] tipo de colheita  [N] nível de perda")
    filtro = v.ler_opcao("   Opção: ", ("T", "A", "C", "N"))
    enriquecidas = colheitas_enriquecidas(estado)
    if filtro == "A":
        codigo = v.ler_codigo_talhao("   Código do talhão: ")
        return [c for c in enriquecidas if c["codigo_talhao"] == codigo]
    if filtro == "C":
        tipo = v.ler_opcao("   MEC ou MAN: ", tuple(calculos.TIPOS_COLHEITA))
        return [c for c in enriquecidas if c["tipo"] == tipo]
    if filtro == "N":
        niveis = tuple(f[1] for f in calculos.FAIXAS_PERDA)
        nivel = v.ler_opcao(f"   Nível ({'/'.join(niveis)}): ",
                            niveis + ("MEDIA",))
        nivel = "MÉDIA" if nivel == "MEDIA" else nivel
        return [c for c in enriquecidas if c["nivel"] == nivel]
    return enriquecidas


def imprimir_colheitas(lista):
    colunas = [("ID", 5, ">"), ("Talhão", 7, "<"), ("Data", 10, "<"), ("Tipo", 8, "<"),
               ("Área ha", 8, ">"), ("Perda t/ha", 10, ">"), ("Perda %", 7, ">"),
               ("Nível", 5, "<"), ("Prejuízo", 16, ">")]
    linhas = [(rotulo_id(c), c["codigo_talhao"], ui.data_br(c["data"]),
               calculos.TIPOS_COLHEITA[c["tipo"]], ui.numero_br(c["area_colhida_ha"]),
               ui.numero_br(c["perda_t_ha"]), ui.numero_br(c["perda_pct"]),
               c["nivel"], ui.moeda(c["prejuizo"]))
              for c in sorted(lista, key=lambda x: x["data"])]
    ui.imprimir_tabela(colunas, linhas)
    if linhas:
        total = sum(c["prejuizo"] for c in lista)
        print(f"\n   {len(linhas)} registro(s) | Prejuízo somado: {ui.moeda(total)}"
              "   (IDs com L = pendentes de sincronização)")


def listar_colheitas(estado):
    ui.cabecalho("COLHEITAS REGISTRADAS")
    if not estado["colheitas"]:
        ui.aviso("Nenhuma colheita registrada.")
        ui.pausar()
        return
    lista = filtrar_colheitas(estado)
    print()
    imprimir_colheitas(lista)
    ui.pausar()


def escolher_colheita(estado):
    if not estado["colheitas"]:
        ui.aviso("Nenhuma colheita registrada.")
        return None
    imprimir_colheitas(colheitas_enriquecidas(estado))
    while True:
        rotulo = v.ler_texto("\n   ID da colheita (ENTER cancela): ", obrigatorio=False,
                             tamanho_max=10)
        if not rotulo:
            return None
        colheita = buscar_colheita(estado, rotulo)
        if colheita:
            return colheita
        ui.aviso("ID não encontrado.")


def diagnostico_colheita(estado):
    ui.cabecalho("DIAGNÓSTICO DA COLHEITA")
    colheita = escolher_colheita(estado)
    if colheita:
        exibir_resultado(calculos.enriquecer_colheita(colheita, estado["config"]),
                         estado["config"])
    ui.pausar()


def excluir_colheita(estado):
    ui.cabecalho("EXCLUIR COLHEITA")
    colheita = escolher_colheita(estado)
    if colheita is None or not pode_alterar(estado, colheita["pendente"]):
        return
    if not v.ler_sim_nao(f"   Confirma a exclusão da colheita {rotulo_id(colheita)}? (S/N): "):
        return
    if online(estado) and not colheita["pendente"]:
        try:
            banco.excluir_colheita(estado["conexao"], colheita["id"])
        except oracledb.Error as erro:
            ui.aviso(f"Erro no banco: {str(erro).splitlines()[0]}")
            return
    estado["colheitas"].remove(colheita)
    persistir(estado)
    arquivos.registrar_log("EXCLUSAO_COLHEITA", rotulo_id(colheita))
    ui.sucesso("Colheita excluída.")


# ===========================================================================
# Análises e relatórios
# ===========================================================================

def montar_painel(estado):
    """
    Função: monta as linhas do painel gerencial. As mesmas linhas são
    exibidas na tela e gravadas no relatório .txt.
    Devolve a tupla (linhas, resumo_em_dicionario).
    """
    config = estado["config"]
    dados = colheitas_enriquecidas(estado)
    linhas = []
    if not dados:
        return ["Nenhuma colheita registrada."], {}

    area_total = sum(c["area_colhida_ha"] for c in dados)
    media_geral = sum(c["perda_pct"] * c["area_colhida_ha"] for c in dados) / area_total
    toneladas = sum(c["toneladas_perdidas"] for c in dados)
    prejuizo = sum(c["prejuizo"] for c in dados)
    recuperavel = sum(c["ganho_potencial"] for c in dados)

    linhas += [
        "VISÃO GERAL",
        f"  Amostragens registradas ...... {len(dados)}",
        f"  Área colhida analisada ....... {ui.numero_br(area_total)} ha",
        f"  Perda média (pond. por área) . {ui.numero_br(media_geral)}%",
        f"  Cana deixada no campo ........ {ui.numero_br(toneladas)} t",
        f"  Prejuízo estimado ............ {ui.moeda(prejuizo)}",
        f"  Recuperável atingindo a meta . {ui.moeda(recuperavel)} "
        f"(meta {ui.numero_br(config['meta_perda_pct'], 1)}%)",
        "",
        "MANUAL x MECÂNICA",
    ]
    resumo_tipo = calculos.resumo_por_tipo_colheita(dados)
    maior = max(r["perda_media_pct"] for r in resumo_tipo.values()) or 1
    colunas = [("Tipo", 9, "<"), ("Registros", 9, ">"), ("Área ha", 10, ">"),
               ("Perda %", 7, ">"), ("Prejuízo", 16, ">"), ("", 25, "<")]
    tabela = [(calculos.TIPOS_COLHEITA[t], r["qtd"], ui.numero_br(r["area"]),
               ui.numero_br(r["perda_media_pct"]), ui.moeda(r["prejuizo"]),
               ui.barra(r["perda_media_pct"], maior, 25))
              for t, r in resumo_tipo.items()]
    linhas += ["  " + t for t in ui.formatar_tabela(colunas, tabela)]

    mec, man = resumo_tipo["MEC"], resumo_tipo["MAN"]
    if mec["qtd"] and man["qtd"]:
        diferenca = mec["perda_media_pct"] - man["perda_media_pct"]
        linhas.append(f"  -> A colheita mecânica perde {ui.numero_br(abs(diferenca))} ponto(s) "
                      f"percentual(is) {'a mais' if diferenca >= 0 else 'a menos'} que a manual.")

    linhas += ["", "RANKING DE TALHÕES (do mais crítico ao menos crítico)"]
    ranking = calculos.ranking_talhoes(dados)
    maior = ranking[0][1] or 1
    colunas = [("Pos", 3, ">"), ("Talhão", 8, "<"), ("Perda %", 7, ">"), ("Nível", 5, "<"),
               ("Prejuízo", 16, ">"), ("", 25, "<")]
    tabela = [(pos, cod, ui.numero_br(pct), calculos.classificar_perda(pct)[0],
               ui.moeda(prej), ui.barra(pct, maior, 25))
              for pos, (cod, pct, prej) in enumerate(ranking, start=1)]
    linhas += ["  " + t for t in ui.formatar_tabela(colunas, tabela)]

    causa = calculos.causa_predominante_geral(dados)
    if causa:
        motivo, acao = calculos.RECOMENDACOES[causa]
        linhas += ["", "PRINCIPAL CAUSA DE PERDA NA SAFRA",
                   f"  Tipo predominante: {calculos.NOMES_PERDA[causa]}",
                   textwrap.fill(motivo, 92, initial_indent="  Causa provável ..: ",
                                 subsequent_indent=" " * 21),
                   textwrap.fill(acao, 92, initial_indent="  Ação sugerida ...: ",
                                 subsequent_indent=" " * 21)]

    resumo = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "parametros": {"preco_tonelada": config["preco_tonelada"],
                       "meta_perda_pct": config["meta_perda_pct"]},
        "geral": {"amostragens": len(dados), "area_ha": round(area_total, 2),
                  "perda_media_pct": round(media_geral, 2),
                  "toneladas_perdidas": round(toneladas, 2),
                  "prejuizo_rs": round(prejuizo, 2),
                  "recuperavel_na_meta_rs": round(recuperavel, 2)},
        "por_tipo_colheita": {calculos.TIPOS_COLHEITA[t]: {k: round(val, 2) for k, val in r.items()}
                              for t, r in resumo_tipo.items()},
        "ranking_talhoes": [{"talhao": cod, "perda_pct": round(pct, 2),
                             "prejuizo_rs": round(prej, 2)} for cod, pct, prej in ranking],
        "causa_predominante": calculos.NOMES_PERDA[causa] if causa else None,
    }
    return linhas, resumo


def painel_gerencial(estado):
    ui.cabecalho("PAINEL GERENCIAL DE PERDAS")
    linhas, _ = montar_painel(estado)
    for texto in linhas:
        print(" " + texto)
    ui.pausar()


def exportar_relatorio(estado):
    ui.cabecalho("EXPORTAR RELATÓRIO")
    if not estado["colheitas"]:
        ui.aviso("Nenhuma colheita registrada para exportar.")
        ui.pausar()
        return
    linhas, resumo = montar_painel(estado)
    titulo = ["=" * ui.LARGURA, "COLHEITACERTA - RELATÓRIO DE PERDAS NA COLHEITA DE CANA".center(ui.LARGURA),
              "=" * ui.LARGURA, ""]
    detalhes = ["", "REGISTROS"]
    colunas = [("ID", 5, ">"), ("Talhão", 7, "<"), ("Data", 10, "<"), ("Tipo", 8, "<"),
               ("Perda %", 7, ">"), ("Nível", 5, "<"), ("Prejuízo", 16, ">")]
    tabela = [(rotulo_id(c), c["codigo_talhao"], ui.data_br(c["data"]),
               calculos.TIPOS_COLHEITA[c["tipo"]], ui.numero_br(c["perda_pct"]),
               c["nivel"], ui.moeda(c["prejuizo"]))
              for c in sorted(colheitas_enriquecidas(estado), key=lambda x: x["data"])]
    detalhes += ["  " + t for t in ui.formatar_tabela(colunas, tabela)]

    caminho_txt = arquivos.exportar_relatorio_txt(titulo + linhas + detalhes)
    caminho_json = arquivos.exportar_resumo_json(resumo)
    arquivos.registrar_log("EXPORTACAO", f"{caminho_txt.name}, {caminho_json.name}")
    ui.sucesso(f"Relatório texto: data/{caminho_txt.name}")
    ui.sucesso(f"Resumo JSON ...: data/{caminho_json.name}")
    ui.pausar()


# ===========================================================================
# Sistema
# ===========================================================================

def configuracoes(estado):
    ui.cabecalho("CONFIGURAÇÕES")
    config = estado["config"]
    print(f"   Preço da tonelada de cana ... {ui.moeda(config['preco_tonelada'])}")
    print(f"   Meta de perda aceitável ..... {ui.numero_br(config['meta_perda_pct'], 1)}%")
    print(f"   Área padrão da amostra ...... {ui.numero_br(config['area_amostra_padrao_m2'], 1)} m²")
    print(f"   Servidor Oracle (DSN) ....... {config['dsn']}")
    if not v.ler_sim_nao("\n   Deseja alterar? (S/N): "):
        return
    print("   (ENTER mantém o valor atual)")
    config["preco_tonelada"] = v.ler_float("   Preço da tonelada (R$): ", minimo=1,
                                           maximo=10000, padrao=config["preco_tonelada"])
    config["meta_perda_pct"] = v.ler_float("   Meta de perda (%): ", minimo=0.5, maximo=30,
                                           padrao=config["meta_perda_pct"])
    config["area_amostra_padrao_m2"] = v.ler_float("   Área padrão da amostra (m²): ", minimo=1,
                                                   maximo=1000,
                                                   padrao=config["area_amostra_padrao_m2"])
    config["dsn"] = v.ler_texto("   DSN do Oracle: ", obrigatorio=False,
                                tamanho_max=120) or config["dsn"]
    arquivos.salvar_config(config)
    arquivos.registrar_log("CONFIGURACAO", f"preço {config['preco_tonelada']} "
                                           f"meta {config['meta_perda_pct']}%")
    ui.sucesso("Configurações salvas em config/config.json.")


def conectar_sincronizar(estado):
    ui.cabecalho("CONEXÃO COM O ORACLE")
    if not online(estado):
        estado["conexao"] = tentar_conectar(estado["config"])
        if not online(estado):
            return
        carregar_dados(estado)
    t, c = quantidade_pendentes(estado)
    if t == 0 and c == 0:
        ui.sucesso("Tudo sincronizado. Nenhum registro pendente.")
        return
    print(f"   Pendentes: {t} talhão(ões) e {c} colheita(s).")
    if v.ler_sim_nao("   Enviar agora para o Oracle? (S/N): "):
        try:
            sincronizar(estado)
        except oracledb.Error as erro:
            ui.aviso(f"Erro na sincronização: {str(erro).splitlines()[0]}")


def ver_log():
    ui.cabecalho("ÚLTIMAS OPERAÇÕES (data/log_operacoes.txt)")
    linhas = arquivos.ler_ultimas_linhas_log(20)
    if not linhas:
        ui.aviso("Log vazio.")
    for texto in linhas:
        print("   " + texto)
    ui.pausar()


def exibir_menu(estado):
    ui.limpar_tela()
    status = "ONLINE (Oracle)" if online(estado) else "OFFLINE (base local)"
    t, c = quantidade_pendentes(estado)
    pend = f" | {t + c} pendente(s)" if t + c else ""
    ui.cabecalho("COLHEITACERTA - Monitor de Perdas na Colheita de Cana",
                 f"{status} | {len(estado['talhoes'])} talhão(ões) | "
                 f"{len(estado['colheitas'])} colheita(s){pend}")
    secao_atual = None
    for codigo, descricao, secao in OPCOES_MENU:
        if secao != secao_atual:
            print(f"\n  {secao}")
            secao_atual = secao
        print(f"   [{codigo:>2}] {descricao}")
    print()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    arquivos.garantir_pastas()
    estado = {"conexao": None, "talhoes": {}, "colheitas": [], "config": arquivos.carregar_config()}

    ui.limpar_tela()
    ui.cabecalho("COLHEITACERTA", "Redução de perdas na colheita de cana-de-açúcar")
    if v.ler_sim_nao("   Conectar ao banco Oracle agora? (S/N): "):
        estado["conexao"] = tentar_conectar(estado["config"])
    else:
        ui.aviso("Modo OFFLINE: os dados serão sincronizados quando houver conexão (opção 12).")
    carregar_dados(estado)
    t, c = quantidade_pendentes(estado)
    if online(estado) and (t or c):
        conectar_sincronizar(estado)
    ui.pausar()

    # Dicionário que associa cada opção do menu à função correspondente
    acoes = {
        "1": cadastrar_talhao, "2": listar_talhoes, "3": editar_talhao, "4": excluir_talhao,
        "5": registrar_colheita, "6": listar_colheitas, "7": diagnostico_colheita,
        "8": excluir_colheita, "9": painel_gerencial, "10": exportar_relatorio,
        "11": configuracoes, "12": conectar_sincronizar,
    }
    opcoes_validas = tuple(op[0] for op in OPCOES_MENU)

    while True:
        exibir_menu(estado)
        opcao = v.ler_opcao("   Escolha uma opção: ", opcoes_validas)
        if opcao == "0":
            break
        ui.limpar_tela()
        if opcao == "13":
            ver_log()
            continue
        acoes[opcao](estado)
        if opcao in ("1", "3", "4", "5", "8", "11", "12"):
            ui.pausar()

    if online(estado):
        estado["conexao"].close()
    arquivos.registrar_log("ENCERRAMENTO", "")
    print("\n   Até a próxima safra! Dados salvos.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n   Programa interrompido pelo usuário. Dados já salvos foram mantidos.\n")
