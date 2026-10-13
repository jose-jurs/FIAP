"""
banco.py
Conexão e operações no banco de dados Oracle (biblioteca oracledb, modo thin).

Tabelas:
  T_CC_TALHAO   -> cadastro dos talhões (áreas de plantio)
  T_CC_COLHEITA -> amostragens de perda realizadas em cada colheita
"""
from datetime import date

import oracledb

import calculos

DDL_TALHAO = """
CREATE TABLE T_CC_TALHAO (
    cd_talhao     VARCHAR2(10)  CONSTRAINT pk_cc_talhao PRIMARY KEY,
    nm_fazenda    VARCHAR2(60)  NOT NULL,
    nr_area_ha    NUMBER(10,2)  NOT NULL CONSTRAINT ck_cc_talhao_area CHECK (nr_area_ha > 0),
    ds_variedade  VARCHAR2(30),
    dt_cadastro   DATE DEFAULT SYSDATE NOT NULL
)"""

DDL_COLHEITA = """
CREATE TABLE T_CC_COLHEITA (
    id_colheita           NUMBER GENERATED ALWAYS AS IDENTITY
                          CONSTRAINT pk_cc_colheita PRIMARY KEY,
    cd_talhao             VARCHAR2(10) NOT NULL
                          CONSTRAINT fk_cc_colheita_talhao REFERENCES T_CC_TALHAO (cd_talhao),
    dt_colheita           DATE         NOT NULL,
    tp_colheita           VARCHAR2(3)  NOT NULL
                          CONSTRAINT ck_cc_colheita_tipo CHECK (tp_colheita IN ('MEC', 'MAN')),
    nr_area_colhida_ha    NUMBER(10,2) NOT NULL,
    nr_produtividade_t_ha NUMBER(10,2) NOT NULL,
    nr_area_amostra_m2    NUMBER(10,2) NOT NULL,
    kg_cana_inteira       NUMBER(10,3) DEFAULT 0 NOT NULL,
    kg_rebolos            NUMBER(10,3) DEFAULT 0 NOT NULL,
    kg_tocos              NUMBER(10,3) DEFAULT 0 NOT NULL,
    kg_lascas             NUMBER(10,3) DEFAULT 0 NOT NULL,
    nr_perda_pct          NUMBER(6,2),
    vl_prejuizo           NUMBER(14,2)
)"""


def conectar(usuario, senha, dsn):
    """Abre e devolve a conexão com o Oracle (lança oracledb.Error se falhar)."""
    return oracledb.connect(user=usuario, password=senha, dsn=dsn)


def tabela_existe(conexao, nome_tabela):
    with conexao.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = :nome",
                       {"nome": nome_tabela.upper()})
        return cursor.fetchone()[0] > 0


def criar_tabelas(conexao):
    """Procedimento: cria as tabelas na primeira execução."""
    with conexao.cursor() as cursor:
        if not tabela_existe(conexao, "T_CC_TALHAO"):
            cursor.execute(DDL_TALHAO)
        if not tabela_existe(conexao, "T_CC_COLHEITA"):
            cursor.execute(DDL_COLHEITA)
    conexao.commit()


# ------------------------------- TALHÕES -----------------------------------

def carregar_talhoes(conexao):
    """Devolve um dicionário {código: dados do talhão} lido do banco."""
    talhoes = {}
    with conexao.cursor() as cursor:
        cursor.execute("""SELECT cd_talhao, nm_fazenda, nr_area_ha, ds_variedade
                            FROM T_CC_TALHAO ORDER BY cd_talhao""")
        for codigo, fazenda, area, variedade in cursor:
            talhoes[codigo] = {
                "fazenda": fazenda,
                "area_ha": float(area),
                "variedade": variedade or "",
                "pendente": False,
            }
    return talhoes


def inserir_talhao(conexao, codigo, talhao):
    with conexao.cursor() as cursor:
        cursor.execute("""INSERT INTO T_CC_TALHAO (cd_talhao, nm_fazenda, nr_area_ha, ds_variedade)
                          VALUES (:cod, :faz, :area, :var)""",
                       {"cod": codigo, "faz": talhao["fazenda"],
                        "area": talhao["area_ha"], "var": talhao["variedade"] or None})
    conexao.commit()


def atualizar_talhao(conexao, codigo, talhao):
    with conexao.cursor() as cursor:
        cursor.execute("""UPDATE T_CC_TALHAO
                             SET nm_fazenda = :faz, nr_area_ha = :area, ds_variedade = :var
                           WHERE cd_talhao = :cod""",
                       {"cod": codigo, "faz": talhao["fazenda"],
                        "area": talhao["area_ha"], "var": talhao["variedade"] or None})
    conexao.commit()


def excluir_talhao(conexao, codigo):
    with conexao.cursor() as cursor:
        cursor.execute("DELETE FROM T_CC_TALHAO WHERE cd_talhao = :cod", {"cod": codigo})
    conexao.commit()


# ------------------------------- COLHEITAS ---------------------------------

def carregar_colheitas(conexao):
    """Devolve a lista de colheitas (tabela de memória) lida do banco."""
    colheitas = []
    with conexao.cursor() as cursor:
        cursor.execute("""SELECT id_colheita, cd_talhao, dt_colheita, tp_colheita,
                                 nr_area_colhida_ha, nr_produtividade_t_ha, nr_area_amostra_m2,
                                 kg_cana_inteira, kg_rebolos, kg_tocos, kg_lascas
                            FROM T_CC_COLHEITA ORDER BY dt_colheita, id_colheita""")
        for linha in cursor:
            (id_col, codigo, data_col, tipo, area_col, produtiv, area_amostra,
             kg_inteira, kg_rebolos, kg_tocos, kg_lascas) = linha
            colheitas.append({
                "id": int(id_col),
                "codigo_talhao": codigo,
                "data": data_col.date().isoformat(),
                "tipo": tipo,
                "area_colhida_ha": float(area_col),
                "produtividade_t_ha": float(produtiv),
                "area_amostra_m2": float(area_amostra),
                "perdas_kg": {
                    "cana_inteira": float(kg_inteira),
                    "rebolos": float(kg_rebolos),
                    "tocos": float(kg_tocos),
                    "lascas": float(kg_lascas),
                },
                "pendente": False,
            })
    return colheitas


def inserir_colheita(conexao, colheita, config):
    """Insere a colheita e devolve o ID gerado pelo Oracle."""
    calculada = calculos.enriquecer_colheita(colheita, config)
    with conexao.cursor() as cursor:
        id_gerado = cursor.var(oracledb.NUMBER)
        cursor.execute("""
            INSERT INTO T_CC_COLHEITA (
                cd_talhao, dt_colheita, tp_colheita, nr_area_colhida_ha,
                nr_produtividade_t_ha, nr_area_amostra_m2, kg_cana_inteira,
                kg_rebolos, kg_tocos, kg_lascas, nr_perda_pct, vl_prejuizo)
            VALUES (:cod, :dt, :tp, :area, :prod, :amostra, :k1, :k2, :k3, :k4, :pct, :prej)
            RETURNING id_colheita INTO :novo_id""",
            {
                "cod": colheita["codigo_talhao"],
                "dt": date.fromisoformat(colheita["data"]),
                "tp": colheita["tipo"],
                "area": colheita["area_colhida_ha"],
                "prod": colheita["produtividade_t_ha"],
                "amostra": colheita["area_amostra_m2"],
                "k1": colheita["perdas_kg"]["cana_inteira"],
                "k2": colheita["perdas_kg"]["rebolos"],
                "k3": colheita["perdas_kg"]["tocos"],
                "k4": colheita["perdas_kg"]["lascas"],
                "pct": round(calculada["perda_pct"], 2),
                "prej": round(calculada["prejuizo"], 2),
                "novo_id": id_gerado,
            })
        novo_id = int(id_gerado.getvalue()[0])
    conexao.commit()
    return novo_id


def excluir_colheita(conexao, id_colheita):
    with conexao.cursor() as cursor:
        cursor.execute("DELETE FROM T_CC_COLHEITA WHERE id_colheita = :id", {"id": id_colheita})
    conexao.commit()
