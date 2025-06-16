# Planejamento de Funcionalidades Avançadas - Racing Analyzer Pro

Este documento detalha as funcionalidades avançadas planejadas para aprimorar o software de análise de telemetria, transformando-o em uma ferramenta de nível profissional para pilotos de simuladores de corrida.

## 1. Análise e Comparação Avançada de Voltas

O objetivo é permitir comparações detalhadas entre múltiplas voltas, sessões e até pilotos (em futuras iterações), fornecendo insights valiosos para melhoria de performance.

**Requisitos:**

*   **Importação Múltipla:**
    *   Permitir ao usuário importar múltiplos arquivos de telemetria (JSON, CSV, LD/LDX) de uma vez, representando diferentes voltas, sessões ou pilotos.
    *   Gerenciar os dados importados de forma organizada, permitindo fácil seleção e agrupamento para análise.
*   **Seleção de Voltas para Comparação:**
    *   Interface intuitiva para selecionar duas ou mais voltas (da mesma sessão ou de sessões diferentes) para comparação lado a lado.
    *   Atribuir cores distintas e personalizáveis a cada volta selecionada para fácil identificação nos gráficos e mapas.
*   **Comparação de Tempos:**
    *   Exibir o tempo total de cada volta selecionada.
    *   Calcular e exibir a diferença de tempo (delta) entre as voltas selecionadas, tanto o delta total quanto o delta acumulado ao longo da pista.
    *   Comparar tempos de setor individuais e exibir deltas por setor.
    *   Identificar automaticamente a volta mais rápida (overall e por setor) dentro do conjunto selecionado.
*   **Comparação de Telemetria:**
    *   Sobrepor gráficos de telemetria (velocidade, RPM, aceleração, freio, ângulo do volante, marcha engatada) das voltas selecionadas.
    *   Exibir um gráfico de "delta time" ao longo da distância/tempo, mostrando onde o tempo foi ganho ou perdido.
    *   Permitir zoom e navegação sincronizada em todos os gráficos e no mapa.
*   **Análise de Traçado (Driving Line):**
    *   Sobrepor as linhas de pilotagem das voltas selecionadas em um mapa 2D da pista.
    *   Visualizar a velocidade, marcha, aceleração e frenagem em pontos específicos do traçado ao passar o mouse.
    *   (Futuro) Calcular e exibir uma linha de pilotagem "ideal" ou "ótima" com base nas melhores seções das voltas analisadas.
    *   Comparar o traçado real com o traçado ideal, destacando áreas de divergência e potencial melhoria.
*   **Identificação de Pontos de Melhoria:**
    *   Algoritmos para sugerir automaticamente pontos específicos onde o piloto pode melhorar (ex: pontos de frenagem, ápice da curva, reaceleração, escolha de marcha).
    *   Comparar a utilização de marchas em curvas específicas entre diferentes voltas.

## 2. Visualização de Dados Aprimorada

Criar uma interface rica, interativa e informativa, facilitando a compreensão dos dados telemétricos.

**Requisitos:**

*   **Dashboard Principal:**
    *   Visão geral da sessão/voltas carregadas (melhor volta, tempos de setor, informações básicas).
*   **Visualização Integrada:**
    *   **Mapa da Pista Interativo:** Exibir o traçado da pista com a posição do carro sincronizada com a timeline e os gráficos. Permitir zoom e pan. Sobreposição de múltiplas voltas com cores distintas.
    *   **Timeline Sincronizada:** Uma linha do tempo (baseada em tempo ou distância) que permite navegar pelos dados da volta. Clicar na timeline atualiza a posição no mapa e nos gráficos.
    *   **Gráficos de Telemetria Configuráveis:**
        *   Exibir múltiplos canais de telemetria simultaneamente (velocidade, RPM, pedais, volante, marchas, forças G, suspensão, etc.).
        *   Permitir ao usuário selecionar quais canais exibir.
        *   Sobreposição de dados de múltiplas voltas com cores distintas.
        *   Zoom interativo e seleção de trechos específicos.
        *   Exibição clara dos valores exatos ao passar o mouse.
*   **Visualização Específica de Pedais e Marchas:**
    *   Gráficos dedicados para a posição do acelerador, freio (e embreagem, se disponível).
    *   Visualização clara da marcha engatada ao longo da volta, sincronizada com outros dados.
*   **Personalização:**
    *   Permitir ao usuário salvar layouts de visualização preferidos.
    *   Opção de escolher cores para as voltas e gráficos.

## 3. Gerenciador e Assistente de Setups

Oferecer ferramentas para gerenciar, compartilhar e até mesmo auxiliar na criação de setups de veículos.

**Requisitos:**

*   **Banco de Dados de Setups:**
    *   Armazenar setups associados a carros e pistas específicas.
    *   Permitir adicionar notas e descrições aos setups.
*   **Importação/Exportação:**
    *   Importar setups de formatos comuns (ex: arquivos .json específicos do simulador, se aplicável).
    *   Exportar setups para compartilhamento ou backup.
*   **Assistente de Criação/Ajuste de Setup (Guiado):**
    *   Interface passo a passo para ajudar usuários menos experientes a criar um setup base ou ajustar um existente.
    *   O usuário descreve o comportamento desejado (ex: "carro mais traseiro nas curvas lentas", "melhorar estabilidade na frenagem", "reduzir subesterço") ou o problema que está enfrentando.
    *   O sistema sugere quais parâmetros ajustar (ex: barras estabilizadoras, pressão dos pneus, aerodinâmica, cambagem, convergência, altura) e em qual direção (aumentar/diminuir).
    *   Fornecer explicações básicas sobre o efeito de cada ajuste.
*   **(Futuro) Sugestões Baseadas em Telemetria:**
    *   Analisar dados de telemetria (ex: temperatura dos pneus, uso da suspensão) para sugerir possíveis ajustes de setup.

## 4. Arquitetura e Extensibilidade

Estruturar o código para facilitar a manutenção, a adição de novas funcionalidades e o suporte a novos simuladores.

**Requisitos:**

*   **Estrutura Modular:**
    *   Separar claramente as responsabilidades: importação de dados, processamento/análise, interface do usuário, gerenciamento de setups.
    *   Utilizar classes e interfaces bem definidas.
*   **Adaptadores de Simulador:**
    *   Criar uma camada de abstração para a importação de dados de diferentes simuladores.
    *   Implementar adaptadores específicos para cada simulador suportado (ACC, LMU, e futuramente iRacing, etc.).
    *   Facilitar a adição de novos adaptadores sem modificar o núcleo da aplicação.
*   **Formato de Dados Interno:**
    *   Definir um formato de dados interno padronizado para representar a telemetria, independentemente do simulador de origem. Os adaptadores serão responsáveis por converter os dados do formato original para este formato interno.
*   **Documentação do Código:**
    *   Manter o código bem comentado e documentado.
*   **Testes:**
    *   Implementar testes unitários e de integração para garantir a robustez das funcionalidades, especialmente para os parsers e módulos de análise.

Este planejamento servirá como guia para as próximas fases de desenvolvimento e refatoração do código.

