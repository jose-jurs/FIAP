-- =====================================================================
-- ColheitaCerta - Script de criação das tabelas (Oracle)
-- Obs.: o programa cria as tabelas automaticamente na primeira conexão.
--       Este script serve para criação manual e para consultas de apoio.
-- =====================================================================

CREATE TABLE T_CC_TALHAO (
    cd_talhao     VARCHAR2(10)  CONSTRAINT pk_cc_talhao PRIMARY KEY,
    nm_fazenda    VARCHAR2(60)  NOT NULL,
    nr_area_ha    NUMBER(10,2)  NOT NULL CONSTRAINT ck_cc_talhao_area CHECK (nr_area_ha > 0),
    ds_variedade  VARCHAR2(30),
    dt_cadastro   DATE DEFAULT SYSDATE NOT NULL
);

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
);

-- ---------------------------------------------------------------------
-- Consultas de apoio
-- ---------------------------------------------------------------------

-- Perda média por tipo de colheita (manual x mecânica)
SELECT tp_colheita,
       COUNT(*)                   AS qtd_amostragens,
       ROUND(AVG(nr_perda_pct), 2) AS perda_media_pct,
       SUM(vl_prejuizo)           AS prejuizo_total
  FROM T_CC_COLHEITA
 GROUP BY tp_colheita;

-- Talhões com perda acima de 10% (nível ALTO)
SELECT c.cd_talhao, t.nm_fazenda, c.dt_colheita, c.nr_perda_pct, c.vl_prejuizo
  FROM T_CC_COLHEITA c
  JOIN T_CC_TALHAO t ON t.cd_talhao = c.cd_talhao
 WHERE c.nr_perda_pct > 10
 ORDER BY c.nr_perda_pct DESC;

-- Para remover as tabelas (ordem importa por causa da FK):
-- DROP TABLE T_CC_COLHEITA;
-- DROP TABLE T_CC_TALHAO;
