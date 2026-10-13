#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Fase 2
Ir Alem (opcional 1): Integracao com API publica de clima (OpenWeather).

O que faz
---------
1. Consulta a previsao do tempo (forecast 5 dias / 3h) para uma cidade.
2. Verifica se ha previsao de CHUVA nas proximas N horas.
3. Imprime um comando de uma letra para voce colar no Monitor Serial do
   ESP32 no Wokwi:
       'C'  -> ha previsao de chuva  -> o ESP32 SUSPENDE a irrigacao.
       'S'  -> sem previsao de chuva -> irrigacao liberada pela logica normal.

Essa e a ponte Python <-> ESP32 descrita no enunciado: como a integracao
automatica no plano gratuito do Wokwi nao e trivial, transferimos o resultado
da API manualmente, digitando a letra no Monitor Serial (Serial.read()).

Como usar
---------
    export OPENWEATHER_API_KEY="sua_chave"
    python3 clima_openweather.py --cidade "Campinas,BR" --horas 12

Sem chave de API o script roda em MODO DEMO (dados simulados), para que a
demonstracao funcione mesmo offline.
"""

import argparse
import os
import sys

try:
    import requests
except ImportError:
    requests = None

API_URL = "https://api.openweathermap.org/data/2.5/forecast"


def consultar_openweather(cidade: str, api_key: str, horas: int):
    """Retorna (vai_chover: bool, detalhe: str) consultando a OpenWeather."""
    params = {
        "q": cidade,
        "appid": api_key,
        "units": "metric",
        "lang": "pt_br",
    }
    resp = requests.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    dados = resp.json()

    # Cada item e uma janela de 3h. Pegamos as proximas 'horas'.
    blocos = max(1, horas // 3)
    proximos = dados.get("list", [])[:blocos]

    vai_chover = False
    chuva_mm = 0.0
    descricoes = []
    for item in proximos:
        rain = item.get("rain", {}).get("3h", 0.0)
        chuva_mm += rain
        desc = item.get("weather", [{}])[0].get("description", "")
        descricoes.append(desc)
        ids = [w.get("id", 0) for w in item.get("weather", [])]
        # Grupos 2xx (tempestade), 3xx (garoa), 5xx (chuva) = chuva.
        if any(200 <= i < 600 for i in ids) or rain > 0:
            vai_chover = True

    detalhe = (f"Cidade: {cidade} | janela: {horas}h | chuva acumulada prevista: "
               f"{chuva_mm:.1f} mm | condicoes: {', '.join(sorted(set(descricoes)))}")
    return vai_chover, detalhe


def modo_demo(cidade: str, horas: int):
    """Fallback sem chave de API: simula uma previsao com chuva leve."""
    detalhe = (f"[MODO DEMO - sem OPENWEATHER_API_KEY] Cidade: {cidade} | "
               f"janela: {horas}h | chuva acumulada prevista: 2.3 mm | "
               f"condicoes: chuva leve")
    return True, detalhe


def main():
    parser = argparse.ArgumentParser(description="FarmTech Fase 2 - previsao de chuva (OpenWeather)")
    parser.add_argument("--cidade", default="Campinas,BR", help="Cidade,PAIS (ex: Campinas,BR)")
    parser.add_argument("--horas", type=int, default=12, help="Horas a olhar na previsao")
    args = parser.parse_args()

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if api_key and requests is not None:
        try:
            vai_chover, detalhe = consultar_openweather(args.cidade, api_key, args.horas)
        except Exception as e:  # falha de rede / cidade invalida -> cai no demo
            print(f"[aviso] Falha ao consultar a API ({e}). Usando MODO DEMO.", file=sys.stderr)
            vai_chover, detalhe = modo_demo(args.cidade, args.horas)
    else:
        if requests is None:
            print("[aviso] Modulo 'requests' nao instalado (pip install requests).", file=sys.stderr)
        vai_chover, detalhe = modo_demo(args.cidade, args.horas)

    comando = "C" if vai_chover else "S"

    print("=" * 60)
    print("FarmTech Solutions - Fase 2 - Previsao de chuva")
    print("=" * 60)
    print(detalhe)
    print("-" * 60)
    if vai_chover:
        print("RESULTADO: HA previsao de chuva -> SUSPENDER irrigacao.")
    else:
        print("RESULTADO: SEM previsao de chuva -> irrigacao liberada.")
    print()
    print(f">>> Cole este caractere no Monitor Serial do ESP32 (Wokwi): {comando}")
    print("=" * 60)


if __name__ == "__main__":
    main()
