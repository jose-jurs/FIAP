/*
 * ============================================================================
 *  FarmTech Solutions - Fase 2
 *  Sistema de Irrigacao Inteligente (ESP32 / Wokwi)
 * ----------------------------------------------------------------------------
 *  Cultura alvo: CAFE (Coffea arabica)
 *
 *  Sensores (substituicoes didaticas pedidas no enunciado):
 *    - 3 botoes verdes  -> niveis de Nitrogenio (N), Fosforo (P), Potassio (K)
 *                          Leitura "tudo ou nada" (pressionado = presente).
 *    - LDR (fotoresistor) -> representa o pH do solo (0 a 14).
 *    - DHT22              -> representa a umidade do SOLO (%).
 *    - Rele azul          -> bomba d'agua da irrigacao.
 *    - LCD I2C 16x2       -> painel de status em tempo real.
 *
 *  As mensagens do Serial sao escritas SEM acentos de proposito, para
 *  evitar problemas de codificacao em diferentes terminais.
 * ============================================================================
 */

#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ----------------------------- Pinagem -------------------------------------
#define PIN_BTN_N   18   // Botao Nitrogenio
#define PIN_BTN_P   19   // Botao Fosforo
#define PIN_BTN_K    5   // Botao Potassio
#define PIN_LDR     34   // LDR (pH)  - ADC1_CH6 (entrada analogica)
#define PIN_DHT     15   // DHT22 (umidade do solo)
#define PIN_RELE    23   // Rele (bomba d'agua)
// LCD I2C usa SDA=21 e SCL=22 (padrao do ESP32)

#define DHTTYPE DHT22
DHT dht(PIN_DHT, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ------------------------- Parametros da cultura (CAFE) --------------------
// Faixas agronomicas de referencia para o cafe (documentadas no README):
const float PH_MIN      = 5.0;   // cafe gosta de solo levemente acido
const float PH_MAX      = 6.5;
const float UMID_SECO   = 40.0;  // abaixo disso: solo seco -> considerar irrigar
const float UMID_UMIDO  = 60.0;  // acima disso: solo ok -> desligar bomba
// Histerese entre 40% e 60% evita o rele ficar ligando/desligando sem parar.

// ------------------------- Estado global -----------------------------------
bool  bombaLigada     = false;   // estado atual da bomba (histerese)
bool  chuvaPrevista   = false;   // alimentado pelo "Ir Alem 1" (Python/Serial)
unsigned long ultimaLeitura = 0;
const unsigned long INTERVALO = 2000; // ms entre leituras

// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(PIN_BTN_N, INPUT_PULLUP);
  pinMode(PIN_BTN_P, INPUT_PULLUP);
  pinMode(PIN_BTN_K, INPUT_PULLUP);
  pinMode(PIN_RELE, OUTPUT);
  digitalWrite(PIN_RELE, LOW);

  dht.begin();

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("FarmTech Fase 2");
  lcd.setCursor(0, 1);
  lcd.print("Irrigacao CAFE");

  Serial.println(F("=============================================="));
  Serial.println(F("FarmTech Solutions - Fase 2 - Irrigacao CAFE"));
  Serial.println(F("Serial: envie 'C' = chuva prevista | 'S' = sem chuva"));
  Serial.println(F("=============================================="));
  delay(1500);
}

// ---------------------------------------------------------------------------
// Le o LDR e converte para uma escala de pH (0 a 14).
float lerPH() {
  int bruto = analogRead(PIN_LDR);           // 0 .. 4095 no ESP32
  float ph = (bruto / 4095.0) * 14.0;        // mapeia para 0 .. 14
  return ph;
}

// Le comandos de chuva enviados pelo Monitor Serial (Ir Alem 1).
void lerSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'C' || c == 'c') {
      chuvaPrevista = true;
      Serial.println(F(">> Previsao: CHUVA. Irrigacao suspensa para economizar agua."));
    } else if (c == 'S' || c == 's') {
      chuvaPrevista = false;
      Serial.println(F(">> Previsao: SEM chuva. Irrigacao liberada pela logica normal."));
    }
  }
}

// ---------------------------------------------------------------------------
// Nucleo da decisao de irrigacao (logica do grupo, documentada no README).
//  Entradas: umidade do solo, pH, contagem de NPK e previsao de chuva.
bool decidirBomba(float umidade, float ph, int npk) {
  bool phOk = (ph >= PH_MIN && ph <= PH_MAX);

  // Cafe bem nutrido (N, P e K presentes) consome mais agua: antecipa a rega.
  float limiarSeco = (npk == 3) ? 45.0 : UMID_SECO;

  // 1) Chuva prevista vence tudo: nao irriga.
  if (chuvaPrevista) return false;

  // 2) Solo ja umido: desliga.
  if (umidade >= UMID_UMIDO) return false;

  // 3) Solo seco: so irriga se o pH estiver na faixa do cafe.
  if (umidade < limiarSeco) {
    return phOk;   // pH fora da faixa -> nao adianta regar, corrigir pH antes
  }

  // 4) Zona morta (entre limiarSeco e UMID_UMIDO): mantem o estado atual.
  return bombaLigada;
}

// ---------------------------------------------------------------------------
void loop() {
  lerSerial();

  if (millis() - ultimaLeitura < INTERVALO) return;
  ultimaLeitura = millis();

  // --- Leitura dos nutrientes (INPUT_PULLUP: pressionado = LOW = presente) ---
  bool n = (digitalRead(PIN_BTN_N) == LOW);
  bool p = (digitalRead(PIN_BTN_P) == LOW);
  bool k = (digitalRead(PIN_BTN_K) == LOW);
  int  npk = (n ? 1 : 0) + (p ? 1 : 0) + (k ? 1 : 0);

  // --- Leitura do pH (LDR) e da umidade do solo (DHT22) ---
  float ph = lerPH();
  float umidade = dht.readHumidity();
  if (isnan(umidade)) umidade = 0.0;   // seguranca se o DHT falhar

  // --- Decisao ---
  bombaLigada = decidirBomba(umidade, ph, npk);
  digitalWrite(PIN_RELE, bombaLigada ? HIGH : LOW);

  bool phOk = (ph >= PH_MIN && ph <= PH_MAX);

  // --- Saida no Monitor Serial ---
  Serial.println(F("----------------------------------------------"));
  Serial.printf("NPK  -> N:%s  P:%s  K:%s  (%d/3)\n",
                n ? "SIM" : "nao", p ? "SIM" : "nao", k ? "SIM" : "nao", npk);
  Serial.printf("pH (LDR)     : %.1f  [%s]\n", ph, phOk ? "OK" : "FORA DA FAIXA");
  Serial.printf("Umidade solo : %.1f %%\n", umidade);
  Serial.printf("Chuva prev.  : %s\n", chuvaPrevista ? "SIM" : "nao");
  Serial.printf("BOMBA        : %s\n", bombaLigada ? ">>> LIGADA <<<" : "desligada");
  if (npk < 2)  Serial.println(F("ALERTA: nutrientes insuficientes - aplicar adubacao NPK."));
  if (!phOk)    Serial.println(F("ALERTA: pH fora da faixa ideal do cafe (5.0 a 6.5)."));

  // --- Painel no LCD ---
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.printf("U:%2.0f%% pH:%.1f", umidade, ph);
  lcd.setCursor(0, 1);
  lcd.printf("NPK:%d/3 %s", npk, bombaLigada ? "BOMBA ON" : "bomba off");
}
