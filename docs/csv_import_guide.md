## Importando Dados de Telemetria CSV do MoTeC

O Race Telemetry Analyzer agora suporta robustamente a importação de arquivos CSV exportados do MoTeC, permitindo análise detalhada de dados de telemetria mesmo quando os formatos binários (.ld) apresentam problemas de compatibilidade.

### Estrutura do Arquivo CSV MoTeC

Os arquivos CSV do MoTeC possuem uma estrutura específica:
- **Metadados**: As primeiras linhas contêm informações como pista, veículo, piloto, data, hora, etc.
- **Cabeçalhos**: Uma linha com os nomes dos canais de telemetria
- **Unidades**: Uma linha com as unidades de medida para cada canal
- **Dados**: Linhas subsequentes com os valores de telemetria para cada ponto de tempo

### Como Usar

1. **Importação Direta**:
   ```python
   from parsers.csv_parser import parse_csv_telemetry
   
   # Carrega os dados de telemetria
   telemetry_data = parse_csv_telemetry("/caminho/para/arquivo.csv")
   
   # Acessa os metadados
   track = telemetry_data["metadata"].get("track")
   car = telemetry_data["metadata"].get("car")
   
   # Acessa os canais disponíveis
   channels = telemetry_data["channels"]
   
   # Acessa os dados de telemetria
   data_points = telemetry_data["data_points"]
   
   # Acessa as voltas identificadas
   laps = telemetry_data["laps"]
   ```

2. **Visualização Básica**:
   ```python
   import matplotlib.pyplot as plt
   import numpy as np
   
   # Extrai dados de tempo e velocidade
   times = [point.get("Time", 0) for point in telemetry_data["data_points"]]
   speeds = [point.get("SPEED", 0) for point in telemetry_data["data_points"]]
   
   # Cria um gráfico simples
   plt.figure(figsize=(10, 6))
   plt.plot(times, speeds)
   plt.title("Velocidade vs. Tempo")
   plt.xlabel("Tempo (s)")
   plt.ylabel("Velocidade (km/h)")
   plt.grid(True)
   plt.show()
   ```

3. **Análise de Voltas**:
   ```python
   # Itera pelas voltas identificadas
   for lap in telemetry_data["laps"]:
       lap_number = lap["lap_number"]
       lap_time = lap["lap_time"]
       lap_data = lap["data_points"]
       
       print(f"Volta {lap_number}: {lap_time:.3f}s ({len(lap_data)} pontos)")
       
       # Analisa dados específicos da volta
       max_speed = max([point.get("SPEED", 0) for point in lap_data])
       print(f"  Velocidade máxima: {max_speed} km/h")
   ```

### Canais Comuns em Arquivos CSV MoTeC

Os arquivos CSV do MoTeC geralmente incluem os seguintes canais principais:

- **Time**: Tempo em segundos desde o início da sessão
- **LAP_BEACON**: Marcador de volta (0 ou 1)
- **SPEED**: Velocidade em km/h
- **THROTTLE**: Posição do acelerador em porcentagem
- **BRAKE**: Pressão do freio em porcentagem
- **GEAR**: Marcha engrenada
- **RPMS**: Rotações do motor em RPM
- **G_LAT**: Força G lateral em m/s²
- **G_LON**: Força G longitudinal em m/s²
- **STEERANGLE**: Ângulo do volante em graus

### Exemplo de Script de Teste

O arquivo `src/test_csv_parser.py` demonstra como usar o parser CSV para analisar e visualizar dados de telemetria. Execute-o para ver um exemplo completo:

```bash
python src/test_csv_parser.py
```

Este script gera um gráfico de exemplo mostrando velocidade, acelerador e freio ao longo do tempo, e salva-o em `output/telemetry_plot.png`.

### Notas Importantes

- O parser identifica automaticamente voltas com base no canal LAP_BEACON ou nos marcadores de beacon nos metadados
- Todos os valores numéricos são convertidos para os tipos apropriados (int ou float)
- O parser é robusto contra variações na estrutura do arquivo, como linhas vazias ou campos ausentes
