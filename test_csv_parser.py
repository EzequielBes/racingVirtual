import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from parsers.csv_parser import parse_csv_telemetry

# Caminho para um arquivo CSV de exemplo
csv_file_path = os.path.join(os.path.dirname(__file__), 'exemplos', 'monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv')

try:
    print(f"Tentando parsear o arquivo: {csv_file_path}")
    telemetry_data = parse_csv_telemetry(csv_file_path)
    print("Arquivo CSV parseado com sucesso!")
    print("\nMetadados:")
    for key, value in telemetry_data.get('metadata', {}).items():
        print(f"  {key}: {value}")
    print("\nCanais (primeiros 5):")
    for i, (channel_name, channel_data) in enumerate(telemetry_data.get('channels', {}).items()):
        if i < 5:
            print(f"  {channel_name} (Unidade: {telemetry_data.get('units', {}).get(channel_name, 'N/A')})")
        else:
            break
    print(f"\nTotal de pontos de dados: {len(telemetry_data.get('data_points', []))}")
    print(f"Total de voltas detectadas: {len(telemetry_data.get('laps', []))}")
    if telemetry_data.get('laps'):
        print("\nPrimeira volta (resumo):")
        first_lap = telemetry_data['laps'][0]
        print(f"  Número da Volta: {first_lap.get('lap_number')}")
        print(f"  Tempo de Início: {first_lap.get('start_time')}")
        print(f"  Tempo de Fim: {first_lap.get('end_time')}")
        print(f"  Tempo da Volta: {first_lap.get('lap_time')}")
        print(f"  Pontos de Dados na Volta: {len(first_lap.get('data_points', []))}")

except FileNotFoundError as e:
    print(f"Erro: {e}")
    print("Certifique-se de que o arquivo CSV de exemplo existe no diretório 'exemplos'.")
except Exception as e:
    print(f"Ocorreu um erro ao parsear o CSV: {e}")
    import traceback
    traceback.print_exc()


