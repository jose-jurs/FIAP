# ============================================================================
#  FarmTech Solutions - Fase 2
#  Ir Alem (opcional 2): Analise estatistica em R para decidir a irrigacao.
# ----------------------------------------------------------------------------
#  Le um historico de leituras dos sensores (leituras.csv), calcula
#  estatisticas descritivas e ajusta um modelo de regressao logistica que
#  estima a probabilidade de a bomba precisar ser ligada a partir da umidade,
#  do pH e do NPK. No fim, aplica o modelo a uma leitura nova.
#
#  Execucao:
#     Rscript analise_irrigacao.R
# ============================================================================

arquivo <- "leituras.csv"
if (!file.exists(arquivo)) {
  stop("Arquivo leituras.csv nao encontrado. Rode o script na mesma pasta.")
}

dados <- read.csv(arquivo, stringsAsFactors = FALSE)
dados$npk <- dados$n + dados$p + dados$k

cat("==============================================\n")
cat("FarmTech Fase 2 - Analise de irrigacao (R)\n")
cat("==============================================\n")
cat("Total de leituras:", nrow(dados), "\n\n")

# --- 1) Estatisticas descritivas -------------------------------------------
resumo <- function(x, nome) {
  cat(sprintf("%-14s media=%.2f  dp=%.2f  min=%.2f  max=%.2f  mediana=%.2f\n",
              nome, mean(x), sd(x), min(x), max(x), median(x)))
}
cat("-- Estatisticas descritivas --\n")
resumo(dados$umidade, "Umidade (%)")
resumo(dados$ph,      "pH")
resumo(dados$npk,     "NPK (0-3)")
cat(sprintf("Bomba ligada em %.0f%% das leituras\n\n",
            100 * mean(dados$bomba)))

# --- 2) Correlacao ----------------------------------------------------------
cat("-- Correlacao com o acionamento da bomba --\n")
cat(sprintf("umidade x bomba : %.2f\n", cor(dados$umidade, dados$bomba)))
cat(sprintf("pH x bomba      : %.2f\n", cor(dados$ph, dados$bomba)))
cat(sprintf("NPK x bomba     : %.2f\n\n", cor(dados$npk, dados$bomba)))

# --- 3) Modelo de regressao logistica --------------------------------------
# Probabilidade de ligar a bomba ~ umidade + pH + NPK
modelo <- glm(bomba ~ umidade + ph + npk, data = dados, family = binomial())
cat("-- Coeficientes do modelo logistico --\n")
print(round(coef(modelo), 4))
cat("\n")

# --- 4) Decisao para uma leitura nova --------------------------------------
nova <- data.frame(umidade = 34.0, ph = 5.8, npk = 3)
prob <- predict(modelo, nova, type = "response")
decisao <- ifelse(prob >= 0.5, "LIGAR a bomba", "manter desligada")

cat("-- Leitura nova --\n")
cat(sprintf("umidade=%.1f%%  pH=%.1f  NPK=%d/3\n",
            nova$umidade, nova$ph, nova$npk))
cat(sprintf("Probabilidade estimada de irrigar: %.1f%%\n", 100 * prob))
cat(sprintf("DECISAO (R): %s\n", decisao))
cat("==============================================\n")
