# ============================================================================
# FarmTech Solutions - Analise Estatistica (R)
# ----------------------------------------------------------------------------
# Le o arquivo 'dados.csv' gerado pela aplicacao em Python e calcula
# estatisticas basicas (media, desvio padrao, minimo, maximo e mediana)
# das areas de plantio e do consumo de insumos.
#
# Uso:  Rscript estatisticas.R
# ============================================================================

# ---- 1. Leitura dos dados --------------------------------------------------
arquivo <- "dados.csv"

if (!file.exists(arquivo)) {
  cat("ERRO: arquivo 'dados.csv' nao encontrado.\n")
  cat("Rode antes a aplicacao Python (farmtech.py) e use a opcao\n")
  cat("'Exportar para CSV' para gerar os dados.\n")
  quit(status = 1)
}

dados <- read.csv(arquivo, stringsAsFactors = FALSE, encoding = "UTF-8")

cat("============================================================\n")
cat("        FARMTECH SOLUTIONS - ANALISE ESTATISTICA (R)\n")
cat("============================================================\n\n")
cat("Registros carregados de 'dados.csv':", nrow(dados), "\n\n")
print(dados)
cat("\n")

# ---- 2. Funcao auxiliar de resumo estatistico ------------------------------
resumo <- function(vetor, titulo, unidade) {
  cat("------------------------------------------------------------\n")
  cat(titulo, "\n")
  cat("------------------------------------------------------------\n")
  cat(sprintf("  Quantidade (n) : %d\n", length(vetor)))
  cat(sprintf("  Soma           : %.2f %s\n", sum(vetor), unidade))
  cat(sprintf("  Media          : %.2f %s\n", mean(vetor), unidade))
  # sd() usa desvio padrao amostral (n-1). Para n=1 retorna NA.
  desvio <- if (length(vetor) > 1) sd(vetor) else 0
  cat(sprintf("  Desvio padrao  : %.2f %s\n", desvio, unidade))
  cat(sprintf("  Minimo         : %.2f %s\n", min(vetor), unidade))
  cat(sprintf("  Maximo         : %.2f %s\n", max(vetor), unidade))
  cat(sprintf("  Mediana        : %.2f %s\n", median(vetor), unidade))
  cat("\n")
}

# ---- 3. Estatisticas gerais ------------------------------------------------
resumo(dados$area_m2, "AREA DE PLANTIO (todas as culturas)", "m2")
resumo(dados$litros,  "CONSUMO DE INSUMOS (todas as culturas)", "L")

# ---- 4. Estatisticas por cultura (loop + decisao) --------------------------
cat("============================================================\n")
cat("  ESTATISTICAS POR CULTURA\n")
cat("============================================================\n\n")

for (cultura in unique(dados$cultura)) {
  subconjunto <- dados[dados$cultura == cultura, ]
  cat(sprintf(">> Cultura: %s (%d registro(s))\n",
              cultura, nrow(subconjunto)))
  media_area <- mean(subconjunto$area_m2)
  desvio_area <- if (nrow(subconjunto) > 1) sd(subconjunto$area_m2) else 0
  media_litros <- mean(subconjunto$litros)
  cat(sprintf("   Area media    : %.2f m2 (desvio %.2f)\n",
              media_area, desvio_area))
  cat(sprintf("   Insumo medio  : %.2f L\n\n", media_litros))
}

cat("Analise concluida.\n")
