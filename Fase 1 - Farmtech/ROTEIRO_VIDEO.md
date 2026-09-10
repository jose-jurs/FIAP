# Roteiro do vídeo (até 5 min) — FarmTech Solutions

Grave a tela mostrando o terminal. Sugestão de fala e passos:

## 0:00–0:30 — Abertura
- "Olá, sou [seu nome], RM [número]. Este é o projeto FarmTech Solutions,
  uma aplicação para apoiar a fazenda na migração para a Agricultura Digital."
- "Trabalhamos com duas culturas do estado de São Paulo: café (área
  retangular) e cana-de-açúcar (área trapezoidal)."

## 0:30–2:30 — Aplicação Python
```bash
python3 farmtech.py
```
- Responda `s` para carregar exemplos.
- **Opção 2** (Saída): mostre os registros e os totais.
- **Opção 1** (Entrada): cadastre um café — comprimento 300, largura 50;
  insumo Fosfato, 500 mL/m, rua de 120 m, 40 ruas. Comente o resultado em litros.
- **Opção 3** (Atualizar): altere o registro 1 e mostre que mudou.
- **Opção 4** (Deletar): remova um registro e mostre a lista atualizada.
- **Opção 5** (Exportar): gere o `dados.csv`.
- **Opção 6**: saia.

## 2:30–3:45 — Estatística em R
```bash
Rscript estatisticas.R
```
- Aponte a **média** e o **desvio padrão** das áreas e dos insumos.
- Mostre as estatísticas **por cultura**.

## 3:45–4:45 — Clima em R (Ir além)
```bash
Rscript clima.R
```
- Escolha **1 (Campinas)**.
- Mostre que os dados vêm de uma **API pública (Open-Meteo)** em tempo real:
  temperatura, condição do céu e vento, com a recomendação de manejo.

## 4:45–5:00 — Encerramento
- "Todo o projeto está versionado no GitHub. Obrigado!"

---
**Dicas:** aumente a fonte do terminal antes de gravar. Teste uma vez antes.
Marque o vídeo como **"não listado"** no YouTube e cole o link em
`link_video.txt`.
