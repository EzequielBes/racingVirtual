"""
Wrapper para integrar o ldparser do GitHub no Race Telemetry Analyzer.
Permite ler arquivos .ld de telemetria do MoTec/Assetto Corsa Competizione.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

# Importa o ldparser do GitHub
try:
    from src.parsers.ldparser_github import ldData
except ImportError as e:
    logging.error(f"Erro ao importar ldparser: {e}")
    ldData = None

logger = logging.getLogger(__name__)

def parse_ld_telemetry(filepath: str) -> Dict[str, Any]:
    """
    Parseia um arquivo LD (Motec) usando o ldparser do GitHub.
    
    Args:
        filepath: Caminho para o arquivo .ld
        
    Returns:
        Dicionário com os dados de telemetria parseados
    """
    logger.info(f"Iniciando parse do arquivo LD: {filepath}")
    
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        # Verifica se é um arquivo .ld
        if not filepath.lower().endswith('.ld'):
            raise ValueError(f"Arquivo deve ter extensão .ld: {filepath}")
        
        # Verifica se o ldparser está disponível
        if ldData is None:
            raise ImportError("ldparser não está disponível. Verifique a instalação.")
        
        # Carrega o arquivo LD
        logger.info("Carregando arquivo LD...")
        ld_data = ldData.fromfile(filepath)
        
        if ld_data is None:
            raise ValueError("Não foi possível carregar dados do arquivo LD")
        
        # Verifica se ld_data tem o método __len__ ou é iterável
        try:
            channel_count = len(ld_data) if hasattr(ld_data, '__len__') else len(list(ld_data))
            logger.info(f"Arquivo LD carregado com sucesso. Canais disponíveis: {channel_count}")
        except Exception as e:
            logger.warning(f"Não foi possível contar os canais: {e}")
            channel_count = "desconhecido"
        
        # Lista de canais importantes para telemetria
        important_channels = [
            'Time', 'Speed', 'RPM', 'Gear', 'Throttle', 'Brake', 'Clutch',
            'Steering', 'LapTime', 'LapNumber', 'Fuel', 'TireTempFL', 'TireTempFR',
            'TireTempRL', 'TireTempRR', 'X', 'Y', 'Z', 'Latitude', 'Longitude'
        ]
        
        # Filtra apenas os canais importantes que existem no arquivo
        available_channels = []
        try:
            for channel in important_channels:
                if channel in ld_data:
                    available_channels.append(channel)
                else:
                    logger.debug(f"Canal '{channel}' não encontrado no arquivo")
        except Exception as e:
            logger.warning(f"Erro ao verificar canais: {e}")
            # Tenta listar todos os canais disponíveis
            try:
                available_channels = list(ld_data.keys()) if hasattr(ld_data, 'keys') else []
            except:
                available_channels = []
        
        if not available_channels:
            logger.warning("Nenhum canal importante encontrado, tentando usar todos os canais disponíveis")
            try:
                available_channels = list(ld_data) if hasattr(ld_data, '__iter__') else []
            except Exception as e:
                logger.error(f"Erro ao listar canais: {e}")
                available_channels = []
        
        if not available_channels:
            raise ValueError("Nenhum canal encontrado no arquivo LD")
        
        logger.info(f"Canais selecionados para processamento: {available_channels}")
        
        # Converte para DataFrame para facilitar o processamento
        df_data = {}
        max_length = 0
        
        # Primeiro, encontra o tamanho máximo dos arrays
        for channel_name in available_channels:
            try:
                channel_data = ld_data[channel_name]
                if hasattr(channel_data, 'data') and channel_data.data is not None:
                    data_length = len(channel_data.data)
                    max_length = max(max_length, data_length)
                    logger.debug(f"Canal {channel_name}: {data_length} amostras")
            except Exception as e:
                logger.warning(f"Erro ao ler canal {channel_name}: {e}")
                continue
        
        if max_length == 0:
            raise ValueError("Nenhum dado válido encontrado no arquivo LD")
        
        logger.info(f"Tamanho máximo dos arrays: {max_length}")
        
        # Agora cria os arrays com o mesmo tamanho
        for channel_name in available_channels:
            try:
                channel_data = ld_data[channel_name]
                if not hasattr(channel_data, 'data') or channel_data.data is None:
                    logger.warning(f"Canal {channel_name} não possui dados válidos")
                    df_data[channel_name] = np.full(max_length, np.nan)
                    continue
                
                data = channel_data.data
                
                # Se o array é menor que o máximo, preenche com NaN
                if len(data) < max_length:
                    # Cria um array do tamanho máximo preenchido com NaN
                    padded_data = np.full(max_length, np.nan)
                    padded_data[:len(data)] = data
                    df_data[channel_name] = padded_data
                else:
                    df_data[channel_name] = data
                    
            except Exception as e:
                logger.warning(f"Erro ao processar canal {channel_name}: {e}")
                # Cria array vazio para este canal
                df_data[channel_name] = np.full(max_length, np.nan)
                continue
        
        if not df_data:
            raise ValueError("Nenhum dado foi processado com sucesso")
        
        df = pd.DataFrame(df_data)
        logger.info(f"DataFrame criado com sucesso: {df.shape}")
        
        # Extrai metadados
        metadata = {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'channels': available_channels,
            'total_samples': len(df),
            'duration': df['Time'].max() - df['Time'].min() if 'Time' in df.columns else 0,
            'format': 'LD'
        }
        
        # Detecta voltas baseado na coluna LAP_BEACON
        laps = []
        if 'LAP_BEACON' in df.columns:
            logger.info("Detectando voltas usando LAP_BEACON...")
            
            # Encontra mudanças na coluna LAP_BEACON
            lap_beacon = df['LAP_BEACON'].fillna(0)
            lap_changes = lap_beacon.diff() != 0
            lap_indices = df[lap_changes].index.tolist()
            
            # Adiciona início se não estiver presente
            if 0 not in lap_indices:
                lap_indices.insert(0, 0)
            
            # Adiciona fim se não estiver presente
            if len(df) - 1 not in lap_indices:
                lap_indices.append(len(df) - 1)
            
            # Cria as voltas
            for i in range(len(lap_indices) - 1):
                start_idx = lap_indices[i]
                end_idx = lap_indices[i + 1]
                
                lap_data = df.iloc[start_idx:end_idx + 1]
                
                # Calcula tempo da volta se houver coluna TIME
                lap_time = 0.0
                if 'TIME' in df.columns:
                    time_data = lap_data['TIME'].dropna()
                    if len(time_data) > 1:
                        lap_time = time_data.iloc[-1] - time_data.iloc[0]
                
                lap_info = {
                    'lap_number': i + 1,
                    'start_index': start_idx,
                    'end_index': end_idx,
                    'lap_time': lap_time,
                    'data_points': len(lap_data)
                }
                laps.append(lap_info)
            
            logger.info(f"Detectadas {len(laps)} voltas usando LAP_BEACON")
        
        # Se não encontrou voltas, tenta detectar por padrões de velocidade
        if not laps:
            logger.info("Tentando detectar voltas por padrões de velocidade...")
            
            if 'SPEED' in df.columns:
                speed_data = df['SPEED'].dropna()
                if len(speed_data) > 0:
                    # Detecta pontos onde a velocidade é muito baixa (possível linha de chegada)
                    speed_threshold = speed_data.quantile(0.1)  # 10% mais baixo
                    low_speed_points = df[df['SPEED'] <= speed_threshold].index.tolist()
                    
                    if len(low_speed_points) > 1:
                        # Agrupa pontos próximos
                        lap_indices = [low_speed_points[0]]
                        for point in low_speed_points[1:]:
                            if point - lap_indices[-1] > 100:  # Mínimo 100 pontos entre voltas
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
                            lap_time = 0.0
                            if 'TIME' in df.columns:
                                time_data = lap_data['TIME'].dropna()
                                if len(time_data) > 1:
                                    lap_time = time_data.iloc[-1] - time_data.iloc[0]
                            
                            lap_info = {
                                'lap_number': i + 1,
                                'start_index': start_idx,
                                'end_index': end_idx,
                                'lap_time': lap_time,
                                'data_points': len(lap_data)
                            }
                            laps.append(lap_info)
                        
                        logger.info(f"Detectadas {len(laps)} voltas usando padrões de velocidade")
        
        # Se ainda não encontrou voltas, trata todo o arquivo como uma volta
        if not laps:
            logger.info("Tratando todo o arquivo como uma volta...")
            lap_time = 0.0
            if 'TIME' in df.columns:
                time_data = df['TIME'].dropna()
                if len(time_data) > 1:
                    lap_time = time_data.iloc[-1] - time_data.iloc[0]
            
            lap_info = {
                'lap_number': 1,
                'start_index': 0,
                'end_index': len(df) - 1,
                'lap_time': lap_time,
                'data_points': len(df)
            }
            laps.append(lap_info)
            logger.info("Criada volta única com todos os dados")
        
        # Cria beacons para compatibilidade
        beacons = []
        if 'Time' in df.columns:
            try:
                # Cria beacons a cada segundo
                time_step = 1.0  # 1 segundo
                current_time = df['Time'].min()
                end_time = df['Time'].max()
                
                while current_time <= end_time:
                    # Encontra o índice mais próximo do tempo atual
                    time_diff = np.abs(df['Time'] - current_time)
                    closest_idx = time_diff.idxmin()
                    
                    beacon = {
                        'time': float(current_time),
                        'index': int(closest_idx),
                        'speed': float(df.loc[closest_idx, 'Speed']) if 'Speed' in df.columns else 0,
                        'rpm': float(df.loc[closest_idx, 'RPM']) if 'RPM' in df.columns else 0,
                        'gear': int(df.loc[closest_idx, 'Gear']) if 'Gear' in df.columns else 0,
                        'throttle': float(df.loc[closest_idx, 'Throttle']) if 'Throttle' in df.columns else 0,
                        'brake': float(df.loc[closest_idx, 'Brake']) if 'Brake' in df.columns else 0,
                        'clutch': float(df.loc[closest_idx, 'Clutch']) if 'Clutch' in df.columns else 0
                    }
                    beacons.append(beacon)
                    current_time += time_step
                
                logger.info(f"Criados {len(beacons)} beacons")
            except Exception as e:
                logger.warning(f"Erro ao criar beacons: {e}")
        
        result = {
            'metadata': metadata,
            'data': df,
            'laps': laps,
            'beacons': beacons,
            'channels': available_channels
        }
        
        logger.info(f"Parse LD concluído com sucesso: {len(df)} amostras, {len(laps)} voltas")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao parsear arquivo LD {filepath}: {e}", exc_info=True)
        raise

def process_laps_from_dataframe(df: pd.DataFrame, time_channel: str) -> List[Dict[str, Any]]:
    """
    Processa o DataFrame para identificar voltas.
    
    Args:
        df: DataFrame com os dados
        time_channel: Nome do canal de tempo
        
    Returns:
        Lista de voltas identificadas
    """
    laps = []
    
    # Procura por canal de volta
    lap_channel = None
    for col in df.columns:
        if "lap" in col.lower() or "beacon" in col.lower():
            lap_channel = col
            break
    
    if lap_channel and lap_channel in df.columns:
        # Usa o canal de volta para identificar voltas
        lap_data = df[lap_channel]
        # Converte para numpy array para facilitar operações
        lap_array = lap_data.to_numpy()
        lap_indices = np.where(lap_array == 1)[0].tolist()
        
        if len(lap_indices) > 1:
            # Cria voltas baseadas nos marcadores
            for i in range(len(lap_indices)):
                start_idx = lap_indices[i]
                
                if i < len(lap_indices) - 1:
                    end_idx = lap_indices[i + 1]
                else:
                    end_idx = len(df) - 1
                
                lap_df = df.iloc[start_idx:end_idx + 1]
                
                lap = {
                    "lap_number": i + 1,
                    "start_time": float(lap_df[time_channel].iloc[0]) if time_channel else 0,
                    "end_time": float(lap_df[time_channel].iloc[-1]) if time_channel else 0,
                    "lap_time": float(lap_df[time_channel].iloc[-1] - lap_df[time_channel].iloc[0]) if time_channel else 0,
                    "data_points": []
                }
                
                # Converte DataFrame para lista de dicionários
                for _, row in lap_df.iterrows():
                    point = {}
                    for col in lap_df.columns:
                        value = row[col]
                        if pd.isna(value):
                            point[col] = None
                        else:
                            point[col] = float(value) if isinstance(value, (int, float)) else str(value)
                    lap["data_points"].append(point)
                
                laps.append(lap)
    
    # Se não encontrou voltas, cria uma volta única
    if not laps and len(df) > 0:
        lap = {
            "lap_number": 1,
            "start_time": float(df[time_channel].iloc[0]) if time_channel else 0,
            "end_time": float(df[time_channel].iloc[-1]) if time_channel else 0,
            "lap_time": float(df[time_channel].iloc[-1] - df[time_channel].iloc[0]) if time_channel else 0,
            "data_points": []
        }
        
        # Converte DataFrame para lista de dicionários
        for _, row in df.iterrows():
            point = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    point[col] = None
                else:
                    point[col] = float(value) if isinstance(value, (int, float)) else str(value)
            lap["data_points"].append(point)
        
        laps.append(lap)
        logger.info("Criada volta única com todos os dados")
    
    return laps

def get_available_channels(file_path: str) -> List[str]:
    """
    Retorna a lista de canais disponíveis em um arquivo .ld.
    
    Args:
        file_path: Caminho para o arquivo .ld
        
    Returns:
        Lista de nomes de canais
    """
    if ldData is None:
        return []
    
    try:
        ld_data = ldData.fromfile(file_path)
        return list(ld_data)
    except Exception as e:
        logger.error(f"Erro ao ler canais do arquivo .ld: {e}")
        return [] 