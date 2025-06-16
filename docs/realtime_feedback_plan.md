# Plano de Arquitetura - Feedback em Tempo Real com IA

## 1. Objetivo

Implementar um sistema que analise dados de telemetria (simulados ou de replays, inicialmente) em tempo real (ou pseudo-real-time durante replay) para fornecer feedback imediato ao usuário sobre sua pilotagem, usando alertas visuais e/ou voz sintetizada.

## 2. Arquitetura Proposta

Utilizaremos uma abordagem baseada em **Threads e Sinais/Slots do PyQt** para desacoplar a análise da interface principal e evitar bloqueios.

-   **`RealTimeAnalyzer` (Classe Core):**
    -   Rodará em um `QThread` separado.
    -   Receberá *chunks* de dados de telemetria (ex: dados de um intervalo de tempo do replay).
    -   Manterá o estado da análise (ex: posição na pista, velocidade atual, inputs).
    -   Aplicará regras de IA (inicialmente simples, baseadas em limiares e padrões) para detectar eventos (ex: frenagem antecipada/tardia, erro de tangência, perda de tração).
    -   Emitirá sinais PyQt (`pyqtSignal`) contendo os alertas/feedbacks gerados (ex: `feedback_detected(str)`).
    -   Poderá ter métodos para iniciar, pausar, parar e carregar dados/regras.

-   **`VoiceSynthesizer` (Classe Helper):**
    -   Pode rodar em seu próprio `QThread` ou ser chamado pelo `RealTimeAnalyzer`.
    -   Utilizará `pyttsx3` para síntese de voz offline.
    -   Receberá texto do `RealTimeAnalyzer` (via chamada direta ou sinal) e o falará.
    -   Gerenciará a fila de falas para evitar sobreposição excessiva.

-   **`MainWindow` / Widgets da UI:**
    -   Conectará aos sinais do `RealTimeAnalyzer` (ex: `feedback_detected`).
    -   Receberá os alertas e os exibirá na interface (ex: em um painel de status, pop-up temporário) ou os encaminhará para o `VoiceSynthesizer`.
    -   Controlará o `RealTimeAnalyzer` (iniciar/parar análise, carregar dados de replay).

## 3. Fluxo de Dados (Exemplo com Replay)

1.  Usuário carrega uma volta/sessão na UI.
2.  UI instancia `RealTimeAnalyzer` e o move para um `QThread`.
3.  UI passa os dados da volta (ou um iterador/gerador) para o `RealTimeAnalyzer`.
4.  UI inicia o thread do `RealTimeAnalyzer`.
5.  `RealTimeAnalyzer` processa os dados em *chunks* ou ponto a ponto.
6.  Ao detectar um evento (ex: velocidade muito baixa no ápice da Curva 3), aplica regras.
7.  Se uma regra for acionada, emite um sinal `feedback_detected("Velocidade baixa no ápice da Curva 3")`.
8.  `MainWindow` (ou um widget específico) recebe o sinal.
9.  UI exibe o alerta visualmente.
10. UI (opcionalmente) chama `VoiceSynthesizer.speak("Velocidade baixa no ápice da Curva 3")`.
11. `VoiceSynthesizer` (em seu thread) usa `pyttsx3` para falar o alerta.
12. Processo continua até o fim dos dados ou interrupção pelo usuário.

## 4. Implementação Inicial (Foco)

-   Criar a classe `RealTimeAnalyzer` com a estrutura básica de threading e sinais.
-   Implementar regras simples (ex: detectar velocidade acima/abaixo de um limiar em um ponto específico - pode requerer dados de pista/setores).
-   Integrar `pyttsx3` na classe `VoiceSynthesizer`.
-   Conectar os sinais básicos à UI para exibir alertas em um `QLabel` ou `QStatusBar`.
-   Simular o envio de dados para o `RealTimeAnalyzer` (ex: iterar sobre dados de um `.ldx` já parseado).

## 5. Evoluções Futuras

-   Captura de dados *realmente* em tempo real (requer integração com o simulador via API ou memória compartilhada - escopo complexo).
-   Regras de IA mais sofisticadas (modelos de ML simples, análise de padrões mais complexos).
-   Integração com APIs de voz externas (ElevenLabs).
-   Configurações de usuário para habilitar/desabilitar feedback, tipos de alertas, voz, etc.
-   Associação dos eventos a pontos específicos no mapa da pista (requer integração com visualização de mapa).

