# FarmTech Solutions — Agricultura Digital

Atividade avaliativa (Python + R) — apoio à migração de uma fazenda para a
Agricultura Digital.

## Culturas trabalhadas (principais do estado de São Paulo)
- **Café** — área calculada como **retângulo** (comprimento × largura)
- **Cana-de-açúcar** — área calculada como **trapézio** ((B + b) / 2 × altura)

## Arquivos

| Arquivo | Descrição |
|---|---|
| `farmtech.py` | Aplicação principal em Python (menu, CRUD, cálculos, export CSV) |
| `estatisticas.R` | Lê `dados.csv` e calcula média, desvio padrão e outras estatísticas |
| `clima.R` | **Desafio "Ir além"**: consulta API meteorológica pública (Open-Meteo) |
| `Resumo_Artigo_VANT.docx` | Resumo do artigo da Embrapa (Formação Social) |
| `gerar_resumo.py` | Script que gerou o `.docx` do resumo (Arial 11, margens 2 cm) |
| `dados.csv` | Amostra de dados exportada pelo Python (consumida pelo R) |
| `link_video.txt` | Link do vídeo de demonstração no YouTube (não listado) |

## Como executar

### 1) Aplicação Python
```bash
python3 farmtech.py
```
Menu de opções:
1. **Entrada de dados** — cadastra um plantio (cultura, área e insumo)
2. **Saída de dados** — imprime todos os registros no terminal
3. **Atualizar dado** — altera um registro em qualquer posição do vetor
4. **Deletar dado** — remove um registro de qualquer posição do vetor
5. **Exportar para CSV** — grava `dados.csv` para a análise em R
6. **Sair do programa**

> Dica: ao iniciar, responda `s` para carregar 3 registros de exemplo e
> agilizar a demonstração.

### 2) Estatística em R
```bash
Rscript estatisticas.R
```
Calcula média e desvio padrão (amostral, n−1) das áreas e dos insumos,
no geral e por cultura. Requer o `dados.csv` gerado no passo anterior.

### 3) Clima em R (Ir além)
```bash
Rscript clima.R
```
Conecta-se à API pública **Open-Meteo** (não exige chave), coleta as
condições atuais de uma praça agrícola e exibe temperatura, condição do
céu e vento, além de uma recomendação simples de manejo.

## Estrutura de dados
Os dados ficam organizados em **vetores** (listas paralelas em Python):
`culturas[]`, `areas[]`, `produtos[]`, `litros_insumo[]` — o índice `i`
representa o mesmo registro em todas as listas.

## Requisitos
- Python 3.8+ (biblioteca padrão; `python-docx` só para (re)gerar o resumo)
- R 4.x (`Rscript`) — apenas pacotes base, sem dependências externas
- Conexão com a internet para o `clima.R`

## Versionamento
Projeto versionado no GitHub para simular um ambiente de desenvolvimento
colaborativo em equipe.
