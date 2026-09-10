# 🌱 FarmTech Solutions — Aplicação de Apoio à Agricultura Digital

Projeto desenvolvido para a **Fase 1** do curso de Inteligência Artificial e
Machine Learning (FIAP). A startup fictícia **FarmTech Solutions** foi
contratada por uma fazenda que quer migrar para a **Agricultura Digital**. Esta
aplicação dá o primeiro passo: organiza os dados de plantio, calcula áreas e
insumos e produz análises estatísticas e climáticas.

O projeto é composto por **duas linguagens que trabalham juntas**:

- **Python** — coleta e organiza os dados, calcula área de plantio e manejo de
  insumos, e exporta um arquivo `.csv`.
- **R** — lê esse `.csv` e calcula estatísticas (média e desvio padrão); um
  segundo programa em R consulta uma **API meteorológica pública** em tempo real.

---

## 📑 Sumário

1. [O que a aplicação faz](#-o-que-a-aplicação-faz)
2. [Culturas e figuras geométricas](#-culturas-e-figuras-geométricas)
3. [Estrutura de arquivos](#-estrutura-de-arquivos)
4. [Como as partes conversam](#-como-as-partes-conversam-arquitetura)
5. [Pré-requisitos](#-pré-requisitos)
6. [Passo a passo — instalação (Windows)](#-passo-a-passo--windows)
7. [Passo a passo — instalação (macOS)](#-passo-a-passo--macos)
8. [Como baixar o projeto](#-como-baixar-o-projeto)
9. [Como executar](#-como-executar)
10. [O menu do Python, opção por opção](#-o-menu-do-python-opção-por-opção)
11. [Detalhamento técnico](#-detalhamento-técnico)
12. [Exemplos de saída real](#-exemplos-de-saída-real)
13. [Solução de problemas (FAQ)](#-solução-de-problemas-faq)
14. [Requisitos do enunciado atendidos](#-requisitos-do-enunciado-atendidos)
15. [Versionamento](#-versionamento)

---

## 🎯 O que a aplicação faz

| Recurso | Descrição |
|---|---|
| Cadastro de plantios | Registra plantios de **café** e **cana-de-açúcar** |
| Cálculo de área | Usa uma **figura geométrica diferente** para cada cultura |
| Manejo de insumos | Calcula quantos **litros** de produto serão necessários |
| CRUD completo | Cria, lê, atualiza e deleta registros (menu interativo) |
| Exportação | Gera `dados.csv` para análise em R |
| Estatística (R) | Média, desvio padrão, mínimo, máximo e mediana |
| Clima (R) | Consulta temperatura/vento/céu em tempo real (Open-Meteo) |

---

## 🌾 Culturas e figuras geométricas

O grupo escolheu as **duas principais culturas do estado de São Paulo**:

| Cultura | Figura geométrica | Fórmula da área |
|---|---|---|
| **Café** | Retângulo | `área = comprimento × largura` |
| **Cana-de-açúcar** | Trapézio | `área = ((base_maior + base_menor) / 2) × altura` |

> **Por que figuras diferentes?** O enunciado pede que cada cultura use um
> cálculo próprio. O café costuma ser plantado em talhões retangulares
> regulares; o trapézio representa talhões de formato irregular, comuns em
> áreas de cana. A área é apresentada em **m²** e também convertida em
> **hectares** (÷ 10.000).

---

## 📁 Estrutura de arquivos

```
Fase 1 - Farmtech/
├── farmtech.py              # Aplicação principal em Python (menu + cálculos)
├── estatisticas.R           # Análise estatística (média e desvio) em R
├── clima.R                  # Consulta à API meteorológica (desafio "Ir além")
├── Resumo_Artigo_VANT.docx  # Resumo do artigo (Formação Social)
├── gerar_resumo.py          # Script que gerou o .docx do resumo
├── dados.csv                # Amostra de dados (gerada pelo Python, lida pelo R)
├── link_video.txt           # Link do vídeo de demonstração no YouTube
├── ROTEIRO_VIDEO.md         # Roteiro sugerido para gravar o vídeo
└── README.md                # Este arquivo
```

---

## 🔗 Como as partes conversam (arquitetura)

```
   ┌──────────────┐   exporta    ┌──────────────┐   lê     ┌────────────────┐
   │  farmtech.py │ ───────────► │   dados.csv  │ ───────► │ estatisticas.R │
   │   (Python)   │   opção 5    │   (arquivo)  │          │      (R)       │
   └──────────────┘              └──────────────┘          └────────────────┘

   ┌──────────────┐   internet   ┌──────────────────────────┐
   │   clima.R    │ ───────────► │  API Open-Meteo (pública) │
   │     (R)      │ ◄─────────── │  temperatura, vento, céu   │
   └──────────────┘   JSON       └──────────────────────────┘
```

O `dados.csv` é o **elo** entre Python e R — simula um ambiente de equipe, onde
um time gera o dado e outro o analisa. O `clima.R` é independente e busca dados
externos ao vivo.

---

## ✅ Pré-requisitos

Você precisa de dois programas instalados no computador:

| Programa | Para quê | Versão |
|---|---|---|
| **Python 3** | Rodar `farmtech.py` | 3.8 ou superior |
| **R** | Rodar `estatisticas.R` e `clima.R` | 4.x |

- **Internet** é necessária apenas para o `clima.R` (consulta à API).
- Nenhum pacote extra é necessário: o Python usa só a biblioteca padrão e o R
  usa apenas funções base.

> Para (re)gerar o resumo `.docx` existe o `gerar_resumo.py`, que usa a
> biblioteca `python-docx`. Isso é **opcional** — o `.docx` já vem pronto.

---

## 🪟 Passo a passo — Windows

### 1. Instalar o Python
1. Acesse https://www.python.org/downloads/windows/
2. Baixe o instalador **"Windows installer (64-bit)"**.
3. Execute e, **MUITO IMPORTANTE**, marque a caixa **"Add Python to PATH"**
   na primeira tela, antes de clicar em *Install Now*.
4. Conclua a instalação.

### 2. Instalar o R
1. Acesse https://cran.r-project.org/bin/windows/base/
2. Clique em **"Download R-x.x.x for Windows"** e execute o instalador
   (next → next → finish).
3. Isso instala o comando `Rscript`.

### 3. Abrir o terminal
- Aperte a tecla **Windows**, digite **`cmd`** e abra o **Prompt de Comando**
  (ou o **PowerShell**).

### 4. Testar se instalou
Digite (um por vez):
```cmd
python --version
Rscript --version
```
Se aparecer o número da versão em cada um, está tudo certo. Se der erro em
`Rscript`, veja a seção [FAQ](#-solução-de-problemas-faq).

> No Windows, o comando do Python normalmente é **`python`** (sem o `3`).

---

## 🍎 Passo a passo — macOS

### 1. Python
O macOS já vem com Python 3. Confirme abrindo o **Terminal**
(Launchpad → Terminal) e digitando:
```bash
python3 --version
```
Se não tiver, instale com o Homebrew (`brew install python`) ou pelo
instalador em https://www.python.org/downloads/macos/.

### 2. Instalar o R
**Opção A — com Homebrew** (recomendado se você já usa o brew):
```bash
brew install r
```
**Opção B — instalador oficial:** baixe o `.pkg` em
https://cran.r-project.org/bin/macosx/ e instale (next → next → finish).

### 3. Testar
```bash
python3 --version
Rscript --version
```
Ambos devem mostrar um número de versão.

> No macOS, o comando do Python é **`python3`** (com o `3`).

---

## ⬇️ Como baixar o projeto

Escolha **uma** das opções:

### Opção A — Arquivo ZIP (mais simples, para leigos)
1. Baixe o arquivo `FarmTech_Solutions.zip`.
2. **Descompacte**: no Windows, clique com o botão direito → *Extrair tudo*;
   no Mac, dê dois cliques no arquivo.
3. Guarde a pasta extraída em um lugar fácil (ex.: Área de Trabalho).

### Opção B — Clonar do GitHub (para quem usa git)
```bash
git clone https://github.com/jose-jurs/FIAP.git
cd "FIAP/Fase 1 - Farmtech"
```
> O repositório é **privado**: o git pedirá seu usuário do GitHub e um
> **token** como senha na primeira vez.

---

## ▶️ Como executar

Abra o terminal **dentro da pasta do projeto**. Uma forma fácil de chegar lá:

- **Windows:** abra a pasta no Explorador, clique na barra de endereço, digite
  `cmd` e aperte Enter — o terminal abre já na pasta.
- **macOS:** digite `cd ` (com espaço) no Terminal e arraste a pasta para a
  janela; depois aperte Enter.

Depois, rode **na ordem**:

### 1) Aplicação Python
| Windows | macOS / Linux |
|---|---|
| `python farmtech.py` | `python3 farmtech.py` |

No menu, responda `s` para carregar dados de exemplo e navegue pelas opções.
A **opção 5** gera o `dados.csv`.

### 2) Estatística em R
```bash
Rscript estatisticas.R
```
Lê o `dados.csv` e mostra média, desvio padrão e outras medidas.

### 3) Clima em R (desafio "Ir além")
```bash
Rscript clima.R
```
Escolha **1** (Campinas). Mostra o clima atual vindo da API Open-Meteo.

> **Dica:** o projeto já inclui um `dados.csv` de exemplo, então o
> `estatisticas.R` funciona mesmo que você ainda não tenha exportado nada.

---

## 🧭 O menu do Python, opção por opção

```
MENU DE OPCOES
  1 - Entrada de dados
  2 - Saida de dados (imprimir)
  3 - Atualizar dado (posicao do vetor)
  4 - Deletar dado (posicao do vetor)
  5 - Exportar para CSV (para a app em R)
  6 - Sair do programa
```

- **1 — Entrada de dados:** cadastra um plantio. Pergunta a cultura, coleta as
  medidas do terreno, **calcula a área**, depois pergunta o insumo e
  **calcula os litros necessários**. Adiciona o registro no fim dos vetores.
- **2 — Saída de dados:** imprime uma tabela com todos os registros
  (numerados a partir de 1) e os **totais** (nº de registros, área total e
  insumo total).
- **3 — Atualizar dado:** você informa o número de um registro e reescreve
  todos os seus campos. Há validação: número inexistente é rejeitado.
- **4 — Deletar dado:** remove um registro de qualquer posição. Os registros
  seguintes são reordenados automaticamente.
- **5 — Exportar para CSV:** grava o `dados.csv` que o R consome.
- **6 — Sair do programa:** encerra o loop principal.

Todas as entradas numéricas são **validadas**: se você digitar letra ou um
valor ≤ 0, o programa avisa e pede de novo.

---

## 🔧 Detalhamento técnico

### Estrutura de dados — vetores paralelos
Os dados ficam em **4 listas (vetores) paralelas**, onde o índice `i` é o mesmo
registro em todas:

```python
culturas      = []   # ex.: "Cafe", "Cana-de-acucar"
areas         = []   # área em m²
produtos      = []   # ex.: "Fosfato", "Herbicida"
litros_insumo = []   # litros de insumo necessários
```

| i | culturas | areas | produtos | litros_insumo |
|---|---|---|---|---|
| 0 | Cafe | 20000.0 | Fosfato | 250.0 |
| 1 | Cana-de-acucar | 35000.0 | Herbicida | 105.0 |

Ao deletar ou atualizar, a operação é aplicada ao **mesmo índice nas quatro
listas**, mantendo-as sempre alinhadas.

### Cálculo de área
```
Café (retângulo):  área = comprimento × largura
Cana  (trapézio):  área = ((base_maior + base_menor) / 2) × altura
```

### Cálculo de insumos
```
Café (por rua):
    total_mL = dose_mL_por_metro × comprimento_da_rua × nº_de_ruas
    total_L  = total_mL / 1000

    Exemplo: 500 mL/m × rua de 120 m × 40 ruas
           = 2.400.000 mL = 2.400 L de Fosfato

Cana (por hectare):
    total_L = dose_L_por_hectare × área_em_hectares
```

### Loops e decisão
- O menu é um **loop** `while True` que só encerra na opção 6 (`break`).
- A escolha de cada opção usa uma cadeia de **decisões** `if / elif / else`.
- A leitura validada de números usa loops que repetem até a entrada ser válida.

### Formato do `dados.csv`
```csv
cultura,area_m2,produto,litros
Cafe,20000.00,Fosfato,250.00
Cana-de-acucar,35000.00,Herbicida,105.00
Cafe,15000.00,Fosfato,180.00
```

### Scripts em R
- **`estatisticas.R`** — lê o CSV com `read.csv`, calcula **média** (`mean`),
  **desvio padrão amostral** (`sd`, base n−1), mínimo, máximo e mediana, no
  geral e **por cultura** (um `for` que separa café de cana).
- **`clima.R`** — monta a URL da API **Open-Meteo**, faz a requisição com
  `url()` + `readLines()` (apenas R base, sem pacotes), extrai os campos do
  JSON com expressões regulares e imprime o resultado. Um bloco `if/else`
  gera uma **recomendação de manejo** (ex.: não pulverizar com chuva ou
  vento forte).

---

## 🖥️ Exemplos de saída real

### `farmtech.py` — opção 2 (saída de dados)
```
===== SAIDA DE DADOS (registros cadastrados) =====
#   Cultura             Area (m2) Insumo           Litros (L)
------------------------------------------------------------
1   Cafe                 20000.00 Fosfato              250.00
2   Cana-de-acucar       35000.00 Herbicida            105.00
3   Cafe                 15000.00 Fosfato              180.00
------------------------------------------------------------
  Total de registros: 3
  Area total plantada: 70000.00 m2
  Insumo total: 535.00 L
```

### `estatisticas.R`
```
------------------------------------------------------------
AREA DE PLANTIO (todas as culturas)
------------------------------------------------------------
  Quantidade (n) : 3
  Soma           : 70000.00 m2
  Media          : 23333.33 m2
  Desvio padrao  : 10408.33 m2
  Minimo         : 15000.00 m2
  Maximo         : 35000.00 m2
  Mediana        : 20000.00 m2

>> Cultura: Cafe (2 registro(s))
   Area media    : 17500.00 m2 (desvio 3535.53)
   Insumo medio  : 215.00 L
```

### `clima.R`
```
------------------------------------------------------------
  CONDICOES ATUAIS - CAMPINAS (SP)
------------------------------------------------------------
  Temperatura     : 19.8 C
  Condicao do ceu : Nublado
  Vento           : 9.4 km/h (direcao 26 graus)
------------------------------------------------------------

Recomendacao para o manejo:
  * Condicoes FAVORAVEIS para aplicacao de insumos.
```

---

## ❓ Solução de problemas (FAQ)

**"python não é reconhecido como comando" (Windows)**
O Python não foi adicionado ao PATH. Reinstale marcando **"Add Python to
PATH"**, ou tente `py farmtech.py` no lugar de `python farmtech.py`.

**"python3: command not found" ou "python: command not found"**
No Windows use `python`; no Mac/Linux use `python3`. Se ainda faltar,
instale o Python (seção de pré-requisitos).

**"Rscript não é reconhecido / command not found"**
O R não está no PATH.
- **Windows:** reinstale o R ou adicione a pasta `C:\Program Files\R\R-x.x.x\bin`
  ao PATH do sistema.
- **macOS:** se instalou pelo `.pkg`, feche e reabra o Terminal; com Homebrew,
  rode `brew install r`.

**O `estatisticas.R` diz que não encontrou `dados.csv`**
Rode o `farmtech.py` antes e use a **opção 5** para exportar, **ou** use o
`dados.csv` de exemplo que já acompanha o projeto (rode o R na mesma pasta).

**O `clima.R` não retorna dados**
Verifique a conexão com a internet — ele depende da API Open-Meteo.

**Acentos aparecem estranhos no terminal**
Os programas foram escritos sem acentos nas saídas justamente para evitar
problemas de codificação em diferentes terminais. Se ainda assim ocorrer,
não afeta os cálculos.

**O git pede usuário/senha ao clonar**
O repositório é privado. Informe seu usuário do GitHub e um **token de acesso**
como senha. Alternativa: baixe o `FarmTech_Solutions.zip`.

---

## 📋 Requisitos do enunciado atendidos

- [x] **(a)** Suporte a 2 culturas (café e cana-de-açúcar)
- [x] **(b)** Cálculo de área por figura geométrica (retângulo e trapézio)
- [x] **(c)** Cálculo de manejo de insumos (por rua e por hectare)
- [x] **(d)** Dados organizados em vetores (listas paralelas)
- [x] **(e)** Menu com entrada, saída, atualização, deleção e sair
- [x] **(f)** Rotinas de loop e decisão
- [x] **(g)** Aplicação em R com estatística (média e desvio) + versionamento
- [x] **(h)** Resumo do artigo (Formação Social)
- [x] **Ir além:** API meteorológica pública consultada em R

---

## 🗂️ Versionamento

Projeto versionado no **GitHub** (repositório `jose-jurs/FIAP`, pasta
`Fase 1 - Farmtech`), simulando um ambiente de desenvolvimento colaborativo em
equipe.

---

*FarmTech Solutions — Fase 1 · Curso de IA e Machine Learning (FIAP).*
