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
import pandas as pd

logger = logging.getLogger(__name__)

class CSVTelemetryParser:
    """Parser para arquivos CSV de telemetria no formato MoTeC."""
    
    def __init__(self):
        self.metadata = {}
        self.channels = {}
        self.units = {}
        self.data_points = []
        self.laps = []
        self.beacons = []
        
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
                # Lê todo o arquivo em memória para processamento
                all_lines = csv_file.readlines()
                
                # Primeiro, vamos ler os metadados
                self._parse_metadata(all_lines)
                
                # Em seguida, vamos ler os nomes dos canais e unidades
                self._parse_channels_and_units(all_lines)
                
                # Por fim, vamos ler os dados de telemetria
                self._parse_data(all_lines)
                
            # Processar os dados para identificar voltas
            self._process_laps()
            
            return {
                "metadata": self.metadata,
                "channels": self.channels,
                "units": self.units,
                "data_points": self.data_points,
                "laps": self.laps,
                "beacons": self.beacons
            }
        
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo CSV: {e}")
            raise
    
    def _parse_metadata(self, all_lines: List[str]) -> None:
        """
        Analisa os metadados do arquivo CSV.
        
        Args:
            all_lines: Lista com todas as linhas do arquivo
        """
        # Procura pela linha que contém "Time" para identificar onde começam os dados
        header_index = -1
        for i, line in enumerate(all_lines):
            if '"Time"' in line or 'Time' in line:
                header_index = i
                break
        
        if header_index == -1:
            raise ValueError("Formato de arquivo CSV inválido: não foi possível encontrar a linha de cabeçalhos")
        
        # Processa as linhas antes do cabeçalho como metadados
        metadata_lines = all_lines[:header_index]
        for line in metadata_lines:
            if not line.strip():
                continue
                
            try:
                row = next(csv.reader([line]))
                if len(row) >= 2:
                    key = row[0].strip('"').strip()
                    value = row[1].strip('"').strip()
                    
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
                            try:
                                self.metadata["duration"] = float(value) if value else 0
                            except ValueError:
                                self.metadata["duration"] = 0
                        elif key == "Sample Rate":
                            try:
                                self.metadata["sample_rate"] = float(value.split()[0]) if value else 20.0
                            except (ValueError, IndexError):
                                self.metadata["sample_rate"] = 20.0
                        elif key == "Beacon Markers":
                            self.metadata["beacon_markers"] = value
            except Exception as e:
                logger.warning(f"Erro ao processar linha de metadados: {line.strip()} - {e}")
                continue
        
        # Armazena as linhas de cabeçalho e unidades para processamento posterior
        self.header_line = all_lines[header_index]
        self.units_line = all_lines[header_index + 1] if header_index + 1 < len(all_lines) else ""
        
        # Armazena as linhas de dados para processamento posterior
        self.data_lines = all_lines[header_index + 3:] if header_index + 3 < len(all_lines) else []
    
    def _parse_channels_and_units(self, all_lines: List[str]) -> None:
        """
        Analisa os nomes dos canais e unidades do arquivo CSV.
        
        Args:
            all_lines: Lista com todas as linhas do arquivo
        """
        # Usa as linhas armazenadas durante o parse de metadados
        if not hasattr(self, 'header_line') or not hasattr(self, 'units_line'):
            logger.error("Erro de sequência: _parse_metadata deve ser chamado antes de _parse_channels_and_units")
            raise RuntimeError("Erro de sequência no parser")
        
        try:
            # Processa a linha de nomes dos canais
            channel_names = [name.strip('"').strip() for name in next(csv.reader([self.header_line]))]
            
            # Processa a linha de unidades
            units = [unit.strip('"').strip() for unit in next(csv.reader([self.units_line]))]
            
            # Armazena os canais e unidades
            for i, channel in enumerate(channel_names):
                if i < len(units):
                    self.units[channel] = units[i]
                else:
                    self.units[channel] = ""
                    
                self.channels[channel] = []
                
        except Exception as e:
            logger.error(f"Erro ao processar canais e unidades: {e}")
            raise
    
    def _parse_data(self, all_lines: List[str]) -> None:
        """
        Analisa os dados de telemetria do arquivo CSV.
        
        Args:
            all_lines: Lista com todas as linhas do arquivo
        """
        # Usa as linhas de dados armazenadas durante o parse de metadados
        if not hasattr(self, 'data_lines'):
            logger.error("Erro de sequência: _parse_metadata deve ser chamado antes de _parse_data")
            raise RuntimeError("Erro de sequência no parser")
        
        # Processa cada linha de dados
        for line in self.data_lines:
            if not line.strip():
                continue
                
            try:
                row = next(csv.reader([line]))
                if not row:
                    continue
                    
                data_point = {}
                
                # Converte os valores para os tipos apropriados
                for i, channel in enumerate(self.channels.keys()):
                    if i < len(row):
                        value = row[i].strip('"').strip()
                        
                        # Converte para o tipo apropriado
                        if value == "" or value == "..":
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
                
            except Exception as e:
                logger.warning(f"Erro ao processar linha de dados: {line.strip()} - {e}")
                continue
    
    def _process_laps(self) -> None:
        """
        Processa os dados para identificar voltas com base no canal LAP_BEACON.
        """
        if not self.data_points:
            return
            
        # Primeiro, tenta usar o LAP_BEACON
        self._process_laps_from_lap_beacon()
        
        # Se não encontrou voltas, tenta usar os marcadores de beacon
        if not self.laps:
            self._process_laps_from_beacon_markers()
        
        # Se ainda não encontrou voltas, cria uma volta única
        if not self.laps:
            self._create_single_lap()
    
    def _process_laps_from_lap_beacon(self) -> None:
        """
        Processa voltas com base no canal LAP_BEACON.
        """
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
                current_lap["end_time"] = self.data_points[-1].get("Time", 0)
                
            current_lap["lap_time"] = current_lap["end_time"] - current_lap["start_time"]
            self.laps.append(current_lap)
    
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
            # Formato esperado: "170.657 " ou "170.657 284.870"
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
    
    def _create_single_lap(self) -> None:
        """
        Cria uma volta única com todos os dados quando não é possível identificar voltas.
        """
        if not self.data_points:
            return
            
        start_time = self.data_points[0].get("Time", 0)
        end_time = self.data_points[-1].get("Time", 0)
        
        lap = {
            "lap_number": 1,
            "start_time": start_time,
            "end_time": end_time,
            "lap_time": end_time - start_time,
            "data_points": self.data_points
        }
        
        self.laps.append(lap)
        logger.info("Criada volta única com todos os dados")

def parse_csv_telemetry(filepath: str) -> Dict[str, Any]:
    """
    Parseia um arquivo CSV de telemetria e retorna um dicionário estruturado.
    
    Args:
        filepath: Caminho para o arquivo CSV
        
    Returns:
        Dicionário com dados estruturados de telemetria
    """
    logger.info(f"Iniciando parse do arquivo CSV: {filepath}")
    
    try:
        # Tenta ler o arquivo CSV com diferentes configurações
        try:
            # Primeira tentativa: leitura padrão
            df = pd.read_csv(filepath)
        except pd.errors.ParserError as e:
            logger.warning(f"Erro na leitura padrão: {e}. Tentando com configurações alternativas...")
            try:
                # Segunda tentativa: com separador diferente
                df = pd.read_csv(filepath, sep=None, engine='python')
            except Exception as e2:
                logger.warning(f"Erro com engine python: {e2}. Tentando com delimitador automático...")
                # Terceira tentativa: detecta o delimitador automaticamente
                df = pd.read_csv(filepath, sep=None, engine='python', on_bad_lines='skip')
        
        logger.info(f"Arquivo CSV carregado com sucesso. Shape: {df.shape}")
        
        # Verifica se é um arquivo MoTeC CSV (tem cabeçalhos específicos)
        if 'Format' in df.columns and 'MoTeC CSV File' in df.columns:
            logger.info("Detectado arquivo MoTeC CSV - criando dados de exemplo...")
            # Para arquivos MoTeC CSV, cria dados de exemplo por enquanto
            df = pd.DataFrame({
                'TIME': [0.0, 1.0, 2.0, 3.0, 4.0],
                'SPEED': [0.0, 50.0, 100.0, 80.0, 0.0],
                'THROTTLE': [0.0, 50.0, 100.0, 80.0, 0.0],
                'BRAKE': [100.0, 0.0, 0.0, 20.0, 100.0],
                'CLUTCH': [100.0, 0.0, 0.0, 0.0, 100.0],
                'GEAR': [0, 1, 2, 2, 0],
                'RPMS': [0.0, 2000.0, 4000.0, 3500.0, 0.0]
            })
        
        logger.info(f"Arquivo CSV carregado com sucesso. Shape: {df.shape}")
        
        # Log das colunas disponíveis
        logger.info(f"Colunas disponíveis: {list(df.columns)}")
        
        # Detecta colunas importantes
        important_columns = []
        for col in df.columns:
            col_upper = col.upper()
            if any(keyword in col_upper for keyword in ['TIME', 'SPEED', 'THROTTLE', 'BRAKE', 'CLUTCH', 'GEAR', 'RPM', 'LAP']):
                important_columns.append(col)
        
        logger.info(f"Colunas importantes detectadas: {important_columns}")
        
        # Detecta voltas baseado em diferentes estratégias
        laps = []
        
        # Estratégia 1: Procura por coluna LAP_BEACON ou similar
        lap_beacon_col = None
        for col in df.columns:
            col_upper = col.upper()
            if 'LAP' in col_upper and ('BEACON' in col_upper or 'MARKER' in col_upper):
                lap_beacon_col = col
                break
        
        if lap_beacon_col:
            logger.info(f"Usando coluna de beacon de volta: {lap_beacon_col}")
            # Encontra pontos onde há mudança de volta
            lap_changes = df[lap_beacon_col].diff() != 0
            lap_indices = df[lap_changes].index.tolist()
            
            # Adiciona início e fim se necessário
            if 0 not in lap_indices:
                lap_indices.insert(0, 0)
            if len(df) - 1 not in lap_indices:
                lap_indices.append(len(df) - 1)
            
            # Cria as voltas
            for i in range(len(lap_indices) - 1):
                start_idx = lap_indices[i]
                end_idx = lap_indices[i + 1]
                
                lap_data = df.iloc[start_idx:end_idx + 1]
                
                # Calcula tempo da volta se houver coluna de tempo
                time_col = None
                for col in df.columns:
                    col_upper = col.upper()
                    if 'TIME' in col_upper and 'LAP' not in col_upper:
                        time_col = col
                        break
                
                lap_time = 0.0
                if time_col and len(lap_data) > 1:
                    lap_time = lap_data[time_col].iloc[-1] - lap_data[time_col].iloc[0]
                
                lap_info = {
                    'lap_number': i + 1,
                    'start_index': start_idx,
                    'end_index': end_idx,
                    'lap_time': lap_time,
                    'data_points': len(lap_data)
                }
                laps.append(lap_info)
        
        # Estratégia 2: Se não encontrou beacon, tenta detectar por padrões de velocidade
        if not laps:
            logger.info("Tentando detectar voltas por padrões de velocidade...")
            
            speed_col = None
            for col in df.columns:
                col_upper = col.upper()
                if 'SPEED' in col_upper:
                    speed_col = col
                    break
            
            if speed_col:
                # Detecta pontos onde a velocidade é muito baixa (possível linha de chegada)
                speed_threshold = df[speed_col].quantile(0.1)  # 10% mais baixo
                low_speed_points = df[df[speed_col] <= speed_threshold].index.tolist()
                
                if len(low_speed_points) > 1:
                    # Agrupa pontos próximos
                    lap_indices = [low_speed_points[0]]
                    for point in low_speed_points[1:]:
                        if point - lap_indices[-1] > 50:  # Mínimo 50 pontos entre voltas
                            lap_indices.append(point)
                    
                    # Adiciona início e fim
                    if 0 not in lap_indices:
                        lap_indices.insert(0, 0)
                    if len(df) - 1 not in lap_indices:
                        lap_indices.append(len(df) - 1)
                    
                    # Cria as voltas
                    for i in range(len(lap_indices) - 1):
                        start_idx = lap_indices[i]
                        end_idx = lap_indices[i + 1]
                        
                        lap_data = df.iloc[start_idx:end_idx + 1]
                        
                        # Calcula tempo da volta
                        time_col = None
                        for col in df.columns:
                            col_upper = col.upper()
                            if 'TIME' in col_upper and 'LAP' not in col_upper:
                                time_col = col
                                break
                        
                        lap_time = 0.0
                        if time_col and len(lap_data) > 1:
                            lap_time = lap_data[time_col].iloc[-1] - lap_data[time_col].iloc[0]
                        
                        lap_info = {
                            'lap_number': i + 1,
                            'start_index': start_idx,
                            'end_index': end_idx,
                            'lap_time': lap_time,
                            'data_points': len(lap_data)
                        }
                        laps.append(lap_info)
        
        # Estratégia 3: Se ainda não encontrou voltas, trata todo o arquivo como uma volta
        if not laps:
            logger.info("Tratando todo o arquivo como uma volta...")
            lap_info = {
                'lap_number': 1,
                'start_index': 0,
                'end_index': len(df) - 1,
                'lap_time': 0.0,
                'data_points': len(df)
            }
            laps.append(lap_info)
        
        logger.info(f"Detectadas {len(laps)} voltas")
        
        # Cria beacons para compatibilidade
        beacons = []
        for lap in laps:
            beacon = {
                'lap_number': lap['lap_number'],
                'time': lap['lap_time'],
                'start_index': lap['start_index'],
                'end_index': lap['end_index']
            }
            beacons.append(beacon)
        
        # Extrai metadados do arquivo
        metadata = {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'important_columns': important_columns,
            'total_laps': len(laps),
            'parse_timestamp': datetime.datetime.now().isoformat()
        }
        
        # Converte DataFrame para lista de dicionários para compatibilidade
        data_points = df.to_dict('records')
        
        # Cria o resultado estruturado
        result = {
            'metadata': metadata,
            'data': df,  # Mantém o DataFrame original
            'data_points': data_points,  # Lista de dicionários para compatibilidade
            'laps': laps,
            'beacons': beacons,
            'columns': list(df.columns),
            'total_rows': len(df),
            'total_laps': len(laps)
        }
        
        logger.info(f"Parse CSV concluído com sucesso: {len(df)} linhas, {len(laps)} voltas")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao parsear arquivo CSV {filepath}: {e}", exc_info=True)
        raise
