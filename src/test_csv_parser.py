"""
Script de teste para o parser CSV de telemetria.
Este script demonstra como usar o parser CSV para ler e processar dados de telemetria.
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Adiciona o diretório raiz ao path para importação de módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.csv_parser import parse_csv_telemetry

def main():
    # Caminho para o arquivo CSV de exemplo
    csv_file = "/home/ubuntu/upload/nurburgring-ferrari_296_gt3-4-2025.05.23-21.21.25.csv"
    
    print(f"Analisando arquivo CSV: {csv_file}")
    
    # Analisa o arquivo CSV
    telemetry_data = parse_csv_telemetry(csv_file)
    
    # Exibe informações básicas
    print("\n=== Metadados ===")
    for key, value in telemetry_data["metadata"].items():
        print(f"{key}: {value}")
    
    print(f"\n=== Canais ({len(telemetry_data['channels'])}) ===")
    for i, (channel, unit) in enumerate(telemetry_data["units"].items()):
        print(f"{i+1}. {channel} ({unit})")
    
    print(f"\n=== Pontos de Dados: {len(telemetry_data['data_points'])} ===")
    if telemetry_data["data_points"]:
        print("Primeiro ponto:")
        for key, value in list(telemetry_data["data_points"][0].items())[:10]:
            print(f"  {key}: {value}")
        print("  ...")
    
    print(f"\n=== Voltas: {len(telemetry_data['laps'])} ===")
    for lap in telemetry_data["laps"]:
        print(f"Volta {lap['lap_number']}: {lap['lap_time']:.3f}s ({len(lap['data_points'])} pontos)")
    
    # Gera um gráfico de exemplo
    create_sample_plot(telemetry_data)
    
    print("\nAnálise concluída com sucesso!")

def create_sample_plot(telemetry_data):
    """Cria um gráfico de exemplo com os dados de telemetria."""
    
    # Verifica se há dados suficientes
    if not telemetry_data["data_points"]:
        print("Sem dados suficientes para gerar gráfico.")
        return
    
    # Cria uma figura com dois subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Extrai os dados de tempo, velocidade e acelerador
    times = [point.get("Time", 0) for point in telemetry_data["data_points"]]
    speeds = [point.get("SPEED", 0) for point in telemetry_data["data_points"]]
    throttles = [point.get("THROTTLE", 0) for point in telemetry_data["data_points"]]
    brakes = [point.get("BRAKE", 0) for point in telemetry_data["data_points"]]
    
    # Plota velocidade
    ax1.plot(times, speeds, 'b-', linewidth=1.5, label='Velocidade (km/h)')
    ax1.set_ylabel('Velocidade (km/h)')
    ax1.set_title('Dados de Telemetria - Velocidade vs. Tempo')
    ax1.grid(True)
    ax1.legend()
    
    # Plota acelerador e freio
    ax2.plot(times, throttles, 'g-', linewidth=1.5, label='Acelerador (%)')
    ax2.plot(times, brakes, 'r-', linewidth=1.5, label='Freio (%)')
    ax2.set_xlabel('Tempo (s)')
    ax2.set_ylabel('Porcentagem (%)')
    ax2.set_title('Dados de Telemetria - Acelerador e Freio vs. Tempo')
    ax2.grid(True)
    ax2.legend()
    
    # Adiciona linhas verticais para as voltas
    for lap in telemetry_data["laps"]:
        ax1.axvline(x=lap["start_time"], color='k', linestyle='--', alpha=0.5)
        ax2.axvline(x=lap["start_time"], color='k', linestyle='--', alpha=0.5)
    
    # Ajusta o layout
    plt.tight_layout()
    
    # Salva o gráfico
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "telemetry_plot.png")
    plt.savefig(output_file)
    print(f"Gráfico salvo em: {output_file}")
    
    # Fecha a figura para liberar memória
    plt.close(fig)

if __name__ == "__main__":
    main()
