# ============================================================================
# FarmTech Solutions - Monitoramento Climatico (R)  [DESAFIO "IR ALEM"]
# ----------------------------------------------------------------------------
# Conecta-se a uma API meteorologica publica e gratuita (Open-Meteo,
# https://open-meteo.com -- NAO exige chave de acesso), coleta os dados
# climaticos atuais de uma cidade e exibe as informacoes em texto simples
# no terminal.
#
# Observacao tecnica: para rodar em qualquer maquina sem instalar pacotes,
# a leitura HTTP usa apenas funcoes do R base (url + readLines) e a
# extracao dos campos JSON e feita com expressoes regulares. A estrutura
# de resposta do endpoint 'current_weather' e fixa, o que torna o parsing
# confiavel.
#
# Uso:  Rscript clima.R
# ============================================================================

# ---- 1. Coordenadas das cidades disponiveis --------------------------------
# (algumas praças agricolas importantes do estado de Sao Paulo)
cidades <- list(
  "Campinas"        = c(lat = -22.9056, lon = -47.0608),
  "Ribeirao Preto"  = c(lat = -21.1775, lon = -47.8103),
  "Piracicaba"      = c(lat = -22.7253, lon = -47.6492),
  "Sao Carlos"      = c(lat = -22.0175, lon = -47.8908)
)

# ---- 2. Traducao do codigo de tempo (WMO weather code) ---------------------
descrever_tempo <- function(codigo) {
  tabela <- c(
    "0"  = "Ceu limpo",
    "1"  = "Predominantemente limpo",
    "2"  = "Parcialmente nublado",
    "3"  = "Nublado",
    "45" = "Neblina",
    "48" = "Neblina com geada",
    "51" = "Garoa leve",
    "53" = "Garoa moderada",
    "55" = "Garoa intensa",
    "61" = "Chuva fraca",
    "63" = "Chuva moderada",
    "65" = "Chuva forte",
    "71" = "Neve fraca",
    "80" = "Pancadas de chuva leves",
    "81" = "Pancadas de chuva moderadas",
    "82" = "Pancadas de chuva fortes",
    "95" = "Tempestade",
    "96" = "Tempestade com granizo"
  )
  chave <- as.character(codigo)
  if (chave %in% names(tabela)) tabela[[chave]] else "Condicao desconhecida"
}

# ---- 3. Extrai um campo numerico do JSON via regex -------------------------
extrair_campo <- function(json, campo) {
  padrao <- paste0('"', campo, '":(-?[0-9.]+)')
  achado <- regmatches(json, regexpr(padrao, json))
  if (length(achado) == 0) return(NA)
  as.numeric(sub(padrao, "\\1", achado))
}

# ---- 4. Menu de selecao da cidade ------------------------------------------
cat("============================================================\n")
cat("     FARMTECH SOLUTIONS - MONITORAMENTO CLIMATICO (R)\n")
cat("============================================================\n\n")
cat("Selecione a praca agricola:\n")
nomes <- names(cidades)
for (i in seq_along(nomes)) {
  cat(sprintf("  %d - %s\n", i, nomes[i]))
}

# Le a opcao. Em execucao nao-interativa (sem teclado), assume Campinas (1).
entrada <- suppressWarnings(readLines("stdin", n = 1))
opcao <- suppressWarnings(as.integer(entrada))
if (length(opcao) == 0 || is.na(opcao) || opcao < 1 || opcao > length(nomes)) {
  cat("\n(Opcao invalida ou vazia -> usando Campinas por padrao.)\n")
  opcao <- 1
}
cidade <- nomes[opcao]
coord <- cidades[[cidade]]

# ---- 5. Monta a URL e consulta a API ---------------------------------------
url_api <- sprintf(
  paste0("https://api.open-meteo.com/v1/forecast?",
         "latitude=%.4f&longitude=%.4f&current_weather=true&timezone=auto"),
  coord[["lat"]], coord[["lon"]]
)

cat(sprintf("\nConsultando dados de %s...\n", cidade))
cat(sprintf("Endpoint: %s\n\n", url_api))

conexao <- tryCatch(url(url_api, open = "r"), error = function(e) NULL)
if (is.null(conexao)) {
  cat("ERRO: nao foi possivel conectar a API. Verifique a internet.\n")
  quit(status = 1)
}
json <- tryCatch(paste(readLines(conexao, warn = FALSE), collapse = ""),
                 error = function(e) "")
close(conexao)

if (nchar(json) == 0) {
  cat("ERRO: resposta vazia da API.\n")
  quit(status = 1)
}

# ---- 6. Processa e exibe os dados ------------------------------------------
temperatura <- extrair_campo(json, "temperature")
vento       <- extrair_campo(json, "windspeed")
direcao     <- extrair_campo(json, "winddirection")
codigo      <- extrair_campo(json, "weathercode")

cat("------------------------------------------------------------\n")
cat(sprintf("  CONDICOES ATUAIS - %s (SP)\n", toupper(cidade)))
cat("------------------------------------------------------------\n")
cat(sprintf("  Temperatura     : %.1f C\n", temperatura))
cat(sprintf("  Condicao do ceu : %s\n", descrever_tempo(codigo)))
cat(sprintf("  Vento           : %.1f km/h (direcao %.0f graus)\n",
            vento, direcao))
cat("------------------------------------------------------------\n\n")

# ---- 7. Recomendacao agronomica simples (decisao) --------------------------
cat("Recomendacao para o manejo:\n")
if (!is.na(codigo) && codigo >= 61) {
  cat("  * Chuva prevista/em curso: EVITAR pulverizacao de insumos\n")
  cat("    (risco de lixiviacao e perda do produto).\n")
} else if (!is.na(vento) && vento > 15) {
  cat("  * Vento forte: EVITAR pulverizacao (risco de deriva).\n")
} else if (!is.na(temperatura) && temperatura > 30) {
  cat("  * Temperatura alta: preferir aplicacao no inicio da manha\n")
  cat("    ou fim da tarde (menor evaporacao).\n")
} else {
  cat("  * Condicoes FAVORAVEIS para aplicacao de insumos.\n")
}
cat("\nMonitoramento concluido.\n")
