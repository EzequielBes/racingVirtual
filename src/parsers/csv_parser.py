"""
Parser para arquivos CSV de telemetria no formato MoTeC.

Este módulo implementa um parser para arquivos CSV exportados do MoTeC,
permitindo a leitura de dados de telemetria para análise no Race Telemetry Analyzer.
"""

import csv
import os
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class CSVTelemetryParser:
    """Parser para arquivos CSV de telemetria no formato MoTeC."""
    
    def __init__(self):
        self.metadata = {}
        self.channels = {}
        self.units = {}
        self.data_points = []
        self.laps = []
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analisa um arquivo CSV de telemetria e retorna os dados estruturados.
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            Dicionário com os dados de telemetria estruturados
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                # Primeiro, vamos ler os metadados
                self._parse_metadata(csv_file)
                
                # Em seguida, vamos ler os nomes dos canais e unidades
                self._parse_channels_and_units(csv_file)
                
                # Por fim, vamos ler os dados de telemetria
                self._parse_data(csv_file)
                
            # Processar os dados para identificar voltas
            self._process_laps()
            
            return {
                "metadata": self.metadata,
                "channels": self.channels,
                "units": self.units,
                "data_points": self.data_points,
                "laps": self.laps
            }
        
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo CSV: {e}")
            raise
    
    def _parse_metadata(self, file_obj) -> None:
        """
        Analisa os metadados do arquivo CSV.
        
        Args:
            file_obj: Objeto de arquivo CSV aberto
        """
        # Lê todo o arquivo em memória para processamento
        file_obj.seek(0)
        all_lines = file_obj.readlines()
        
        # Processa as primeiras linhas para metadados
        metadata_lines = all_lines[:12]  # Assumindo que os metadados ocupam as primeiras 12 linhas
        for line in metadata_lines:
            row = next(csv.reader([line]))
            if len(row) >= 2:
                key = row[0].strip('"')
                value = row[1].strip('"')
                
                if key and key != "":
                    self.metadata[key] = value
                    
                    # Tratamento especial para alguns campos
                    if key == "Venue":
                        self.metadata["track"] = value
                    elif key == "Vehicle":
                        self.metadata["car"] = value
                    elif key == "Driver":
                        self.metadata["driver"] = value
                    elif key == "Log Date":
                        self.metadata["date"] = value
                    elif key == "Log Time":
                        self.metadata["time"] = value
                    elif key == "Duration":
                        self.metadata["duration"] = float(value) if value else 0
        
        # Encontra a linha de cabeçalhos
        header_index = -1
        for i, line in enumerate(all_lines):
            row = next(csv.reader([line]))
            if row and row[0].strip('"') == "Time":
                header_index = i
                break
        
        if header_index == -1:
            raise ValueError("Formato de arquivo CSV inválido: não foi possível encontrar a linha de cabeçalhos")
        
        # Armazena as linhas de cabeçalho e unidades para processamento posterior
        self.header_line = all_lines[header_index]
        self.units_line = all_lines[header_index + 1] if header_index + 1 < len(all_lines) else ""
        
        # Armazena as linhas de dados para processamento posterior
        self.data_lines = all_lines[header_index + 3:] if header_index + 3 < len(all_lines) else []
    
    def _parse_channels_and_units(self, file_obj) -> None:
        """
        Analisa os nomes dos canais e unidades do arquivo CSV.
        
        Args:
            file_obj: Objeto de arquivo CSV aberto
        """
        # Usa as linhas armazenadas durante o parse de metadados
        if not hasattr(self, 'header_line') or not hasattr(self, 'units_line'):
            logger.error("Erro de sequência: _parse_metadata deve ser chamado antes de _parse_channels_and_units")
            raise RuntimeError("Erro de sequência no parser")
        
        # Processa a linha de nomes dos canais
        channel_names = [name.strip('"') for name in next(csv.reader([self.header_line]))]
        
        # Processa a linha de unidades
        units = [unit.strip('"') for unit in next(csv.reader([self.units_line]))]
        
        # Armazena os canais e unidades
        for i, channel in enumerate(channel_names):
            if i < len(units):
                self.units[channel] = units[i]
            else:
                self.units[channel] = ""
                
            self.channels[channel] = []
    
    def _parse_data(self, file_obj) -> None:
        """
        Analisa os dados de telemetria do arquivo CSV.
        
        Args:
            file_obj: Objeto de arquivo CSV aberto
        """
        # Usa as linhas de dados armazenadas durante o parse de metadados
        if not hasattr(self, 'data_lines'):
            logger.error("Erro de sequência: _parse_metadata deve ser chamado antes de _parse_data")
            raise RuntimeError("Erro de sequência no parser")
        
        # Processa cada linha de dados
        for line in self.data_lines:
            if not line.strip():
                continue
                
            row = next(csv.reader([line]))
            if not row:
                continue
                
            data_point = {}
            
            # Converte os valores para os tipos apropriados
            for i, channel in enumerate(self.channels.keys()):
                if i < len(row):
                    value = row[i].strip('"')
                    
                    # Converte para o tipo apropriado
                    if value == "":
                        data_point[channel] = None
                    elif "." in value:
                        try:
                            data_point[channel] = float(value)
                        except ValueError:
                            data_point[channel] = value
                    else:
                        try:
                            data_point[channel] = int(value)
                        except ValueError:
                            data_point[channel] = value
                else:
                    data_point[channel] = None
            
            self.data_points.append(data_point)
    
    def _process_laps(self) -> None:
        """
        Processa os dados para identificar voltas com base no canal LAP_BEACON.
        """
        if not self.data_points:
            return
            
        current_lap = {
            "lap_number": 1,
            "start_time": 0,
            "end_time": 0,
            "lap_time": 0,
            "data_points": []
        }
        
        lap_start_time = 0
        in_lap = False
        
        for point in self.data_points:
            time = point.get("Time", 0)
            lap_beacon = point.get("LAP_BEACON", 0)
            
            # Adiciona o ponto à volta atual
            current_lap["data_points"].append(point)
            
            # Verifica se é uma nova volta
            if lap_beacon == 1 and not in_lap:
                in_lap = True
                
                # Se não for a primeira volta, finaliza a anterior
                if current_lap["lap_number"] > 1:
                    current_lap["end_time"] = time
                    current_lap["lap_time"] = time - lap_start_time
                    self.laps.append(current_lap.copy())
                
                # Inicia nova volta
                lap_start_time = time
                current_lap = {
                    "lap_number": len(self.laps) + 1,
                    "start_time": time,
                    "end_time": 0,
                    "lap_time": 0,
                    "data_points": [point]
                }
            elif lap_beacon == 0:
                in_lap = False
        
        # Adiciona a última volta se tiver dados
        if current_lap["data_points"]:
            if "Duration" in self.metadata:
                current_lap["end_time"] = float(self.metadata["Duration"])
            else:
                current_lap["end_time"] = time
                
            current_lap["lap_time"] = current_lap["end_time"] - current_lap["start_time"]
            self.laps.append(current_lap)
        
        # Se não encontrou voltas pelo LAP_BEACON, tenta usar os marcadores de beacon
        if not self.laps and "Beacon Markers" in self.metadata:
            self._process_laps_from_beacon_markers()
    
    def _process_laps_from_beacon_markers(self) -> None:
        """
        Processa voltas com base nos marcadores de beacon nos metadados.
        """
        if "Beacon Markers" not in self.metadata:
            return
            
        # Extrai os tempos dos marcadores de beacon
        beacon_markers_str = self.metadata["Beacon Markers"].strip()
        if not beacon_markers_str:
            return
            
        try:
            # Formato esperado: "00.000 96.877 234.314 375.021 500.098 "
            beacon_times = [float(t) for t in beacon_markers_str.split() if t]
        except ValueError:
            logger.error(f"Formato inválido para marcadores de beacon: {beacon_markers_str}")
            return
        
        if not beacon_times:
            return
            
        # Cria voltas com base nos marcadores de beacon
        for i in range(len(beacon_times)):
            start_time = beacon_times[i]
            
            # Define o fim da volta
            if i < len(beacon_times) - 1:
                end_time = beacon_times[i + 1]
            elif "Duration" in self.metadata:
                end_time = float(self.metadata["Duration"])
            else:
                end_time = self.data_points[-1].get("Time", start_time)
            
            # Filtra os pontos de dados para esta volta
            lap_data_points = [
                point for point in self.data_points
                if start_time <= point.get("Time", 0) < end_time
            ]
            
            lap = {
                "lap_number": i + 1,
                "start_time": start_time,
                "end_time": end_time,
                "lap_time": end_time - start_time,
                "data_points": lap_data_points
            }
            
            self.laps.append(lap)

def parse_csv_telemetry(file_path: str) -> Dict[str, Any]:
    """
    Função auxiliar para analisar um arquivo CSV de telemetria.
    
    Args:
        file_path: Caminho para o arquivo CSV
        
    Returns:
        Dicionário com os dados de telemetria estruturados
    """
    parser = CSVTelemetryParser()
    return parser.parse_file(file_path)
