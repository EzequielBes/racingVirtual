# Race Telemetry Analyzer - Documentação

## Visão Geral

O Race Telemetry Analyzer é uma ferramenta profissional para análise de telemetria de simuladores de corrida, com foco atual no Assetto Corsa Competizione (ACC) e Le Mans Ultimate (LMU). A aplicação permite importar, visualizar, analisar e agora também exportar dados de telemetria para melhorar o desempenho do piloto e facilitar a interoperabilidade com outras ferramentas.

## Formatos Suportados

### Importação
- **MoTeC .ld**: Formato binário com dados detalhados de telemetria
- **MoTeC .ldx**: Formato XML com dados de telemetria
- **MoTeC CSV**: Formato CSV exportado do MoTeC com metadados e canais de telemetria
- **JSON**: Formato genérico para dados de telemetria
- **CSV**: Formato tabular para dados de telemetria

### Exportação
- **MoTeC .ld**: Geração de arquivos binários MoTeC a partir de dados internos ou importados.

## Funcionalidades Principais

### Importação de Dados
- Suporte a múltiplos formatos (.ld, .ldx, MoTeC CSV, JSON, CSV)
- Detecção automática de formato
- Mapeamento flexível de canais de telemetria
- Processamento robusto de metadados e estrutura de arquivos

### Visualização de Traçado e Replay
- Mapa 2D da pista com traçado colorido baseado em dados reais
- Coloração inteligente baseada em:
  - Velocidade (alta/média/baixa)
  - Freio (zonas de frenagem)
  - Acelerador (zonas de aceleração)
- Ghost Replay para comparação de múltiplas voltas
- Controles de playback (play, pause, stop, slider)
- Timeline sincronizada

### Comparação de Voltas
- Comparação visual de múltiplas voltas simultaneamente
- Análise de diferenças de tempo (geral e por setor)
- Identificação de áreas de melhoria

### Coach Virtual
- Interface de chat para perguntas sobre desempenho
- Análise contextualizada baseada nos dados da sessão
- Suporte a LLM local (Ollama) para feedback

### Gerenciamento de Setups
- Importação/exportação de setups
- Interface para visualização e edição de parâmetros
- Assistente guiado para criação de novos setups

### Exportação para MoTeC (.ld)
- **Nova Funcionalidade Validada:** Exporta dados de telemetria selecionados para o formato binário MoTeC .ld.
- Baseado nos módulos do projeto `GeekyDeaks/sim-to-motec` (integrados em `src/stm`).
- Permite selecionar canais específicos para exportação (ex: SPEED, THROTTLE, BRAKE, RPMS, GEAR).
- Útil para converter dados de diferentes fontes para um formato padrão MoTeC ou para preparar dados para análise em MoTeC i2.
- **Importante:** Requer conhecimento dos nomes exatos dos canais no arquivo de origem.
- Funciona de forma independente da interface gráfica, permitindo uso via scripts.

## Requisitos do Sistema

- Python 3.11+
- **Headers de Desenvolvimento Python:** Necessários para compilar a dependência `salsa20`. Instale com `sudo apt-get install python3.11-dev` (Debian/Ubuntu) ou equivalente.
- PyQt6
- PyQtGraph
- NumPy, Pandas
- pyttsx3 (para síntese de voz)
- salsa20 (para compatibilidade com módulos de exportação MoTeC)
- Ollama (para funcionalidade de Coach Virtual)
- Bibliotecas adicionais conforme `requirements.txt`

## Instalação

1. Clone o repositório.
2. **Instale os Headers de Desenvolvimento Python:** `sudo apt-get update && sudo apt-get install -y python3.11-dev` (ou equivalente para seu sistema).
3. **Instale as dependências Python:** `pip install -r requirements.txt`. Se encontrar erros de permissão, tente `pip install --user -r requirements.txt`.
4. Para funcionalidade completa do Coach Virtual, instale Ollama: `curl -fsSL https://ollama.com/install.sh | sh`.
5. Execute a aplicação: `python src/main.py`.

## Uso Básico

1. Inicie a aplicação.
2. Importe um arquivo de telemetria (.ld, .ldx, etc.).
3. Visualize o traçado e os dados de telemetria.
4. Compare voltas adicionando múltiplos arquivos.
5. Use o Ghost Replay para análise visual.
6. Consulte o Coach Virtual para dicas de melhoria.

## Exportando para MoTeC (.ld)

1.  **Identifique os Canais:** Use ferramentas ou scripts (como o `src/list_channels.py` incluído) para listar os nomes exatos dos canais disponíveis no arquivo de telemetria que você deseja exportar.
2.  **Selecione os Canais:** Escolha os canais que deseja incluir no arquivo .ld exportado.
3.  **Prepare os Dados:** Carregue os dados dos canais selecionados usando o parser apropriado (ex: `parsers.ldparser`).
4.  **Crie o Log MoTeC:** Utilize as classes `MotecLog` e `MotecChannel` do módulo `src.stm.motec.ld` para construir o log MoTeC em memória.
    - Preencha as informações do cabeçalho (`driver`, `vehicle`, `venue`, `date`, `time`, etc.).
    - Crie um `MotecChannel` para cada canal selecionado, fornecendo metadados como `id` (único por canal), `name`, `units`, `freq`, `datatype`, `datasize`, etc.
    - Adicione os dados (samples) a cada `MotecChannel`.
5.  **Gere o Arquivo:** Chame o método `to_string()` no objeto `MotecLog` para obter os bytes do arquivo .ld e salve-os em um arquivo.

*Veja o script `src/test_motec_export.py` para um exemplo prático de como realizar a exportação.*

## Desenvolvimento Futuro

- Suporte a mais simuladores (iRacing, etc.)
- Análises avançadas com IA
- Previsão de performance
- Agrupamento de erros com clustering
- Geração automática de plano de treino
- Interface gráfica para a funcionalidade de exportação MoTeC.

## Créditos

- Desenvolvido com base no projeto original de Ezequiel Bes.
- Parser .ld baseado no trabalho de `gotzl/ldparser`.
- Funcionalidade de exportação .ld baseada no trabalho de `GeekyDeaks/sim-to-motec`.

