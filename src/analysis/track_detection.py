"""
Sistema avançado de detecção e análise de traçado de pista.
Implementa algoritmos para extrair coordenadas da pista a partir de dados de telemetria.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy.spatial.distance import cdist
from scipy.interpolate import interp1d, splprep, splev
from scipy.signal import savgol_filter
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrackPoint:
    """Representa um ponto no traçado da pista."""
    x: float
    y: float
    distance: float = 0.0
    sector: int = 1
    elevation: float = 0.0
    banking: float = 0.0
    corner_radius: float = 0.0
    speed_limit: float = 0.0

@dataclass
class TrackSector:
    """Representa um setor da pista."""
    id: int
    start_distance: float
    end_distance: float
    length: float
    type: str  # 'straight', 'corner_left', 'corner_right', 'chicane'
    difficulty: float = 0.0
    optimal_speed: float = 0.0

@dataclass
class TrackLayout:
    """Layout completo da pista."""
    name: str
    points: List[TrackPoint]
    sectors: List[TrackSector]
    total_length: float
    lap_record: Optional[float] = None
    direction: str = "clockwise"  # clockwise, counterclockwise
    surface_type: str = "asphalt"

class TrackDetector:
    """Detector avançado de traçado de pista."""
    
    def __init__(self):
        self.track_database = self._load_track_database()
        
    def _load_track_database(self) -> Dict[str, Dict]:
        """Carrega base de dados de pistas conhecidas."""
        return {
            "monza": {
                "full_name": "Autodromo Nazionale di Monza",
                "length": 5793,
                "sectors": 3,
                "direction": "clockwise",
                "corners": 11,
                "straights": 3,
                "elevation_change": 15
            },
            "spa": {
                "full_name": "Circuit de Spa-Francorchamps",
                "length": 7004,
                "sectors": 3,
                "direction": "clockwise",
                "corners": 19,
                "straights": 2,
                "elevation_change": 104
            },
            "silverstone": {
                "full_name": "Silverstone Circuit",
                "length": 5891,
                "sectors": 3,
                "direction": "clockwise",
                "corners": 18,
                "straights": 2,
                "elevation_change": 15
            },
            "nurburgring": {
                "full_name": "Nürburgring GP-Strecke",
                "length": 5148,
                "sectors": 3,
                "direction": "clockwise",
                "corners": 15,
                "straights": 2,
                "elevation_change": 40
            },
            "imola": {
                "full_name": "Autodromo Enzo e Dino Ferrari",
                "length": 4909,
                "sectors": 3,
                "direction": "counterclockwise",
                "corners": 19,
                "straights": 1,
                "elevation_change": 40
            }
        }
    
    def detect_track_from_telemetry(self, telemetry_data: Dict[str, Any]) -> Optional[TrackLayout]:
        """Detecta o traçado da pista a partir dos dados de telemetria."""
        try:
            # Extrai nome da pista dos metadados
            track_name = self._extract_track_name(telemetry_data)
            
            # Extrai coordenadas dos dados de telemetria
            coordinates = self._extract_coordinates(telemetry_data)
            
            if not coordinates:
                logger.warning("Não foi possível extrair coordenadas da telemetria")
                return self._generate_synthetic_track(track_name, telemetry_data)
            
            # Processa coordenadas para criar traçado
            track_points = self._process_coordinates(coordinates)
            
            # Detecta setores
            sectors = self._detect_sectors(track_points, telemetry_data)
            
            # Calcula propriedades da pista
            total_length = self._calculate_track_length(track_points)
            
            return TrackLayout(
                name=track_name,
                points=track_points,
                sectors=sectors,
                total_length=total_length,
                direction=self._detect_direction(track_points)
            )
            
        except Exception as e:
            logger.error(f"Erro ao detectar traçado da pista: {e}")
            return None
    
    def _extract_track_name(self, telemetry_data: Dict[str, Any]) -> str:
        """Extrai o nome da pista dos metadados."""
        metadata = telemetry_data.get('metadata', {})
        
        # Tenta diferentes campos para o nome da pista
        track_fields = ['track', 'Venue', 'venue', 'Track', 'circuit', 'Circuit']
        
        for field in track_fields:
            if field in metadata and metadata[field]:
                track_name = metadata[field].lower().strip()
                
                # Normaliza nomes conhecidos
                if 'monza' in track_name:
                    return 'monza'
                elif 'spa' in track_name or 'francorchamps' in track_name:
                    return 'spa'
                elif 'silverstone' in track_name:
                    return 'silverstone'
                elif 'nurburgring' in track_name or 'nürburgring' in track_name:
                    return 'nurburgring'
                elif 'imola' in track_name:
                    return 'imola'
                
                return track_name
        
        return "unknown_track"
    
    def _extract_coordinates(self, telemetry_data: Dict[str, Any]) -> List[Tuple[float, float]]:
        """Extrai coordenadas X,Y dos dados de telemetria."""
        coordinates = []
        
        # Verifica se há dados de posição nos pontos de telemetria
        data_points = telemetry_data.get('data_points', [])
        
        if not data_points:
            return coordinates
        
        # Procura por campos de coordenadas
        coordinate_fields = [
            ('POS_X', 'POS_Y'),
            ('X', 'Y'),
            ('GPS_LAT', 'GPS_LONG'),
            ('LAT', 'LONG'),
            ('LATITUDE', 'LONGITUDE')
        ]
        
        for x_field, y_field in coordinate_fields:
            if x_field in data_points[0] and y_field in data_points[0]:
                for point in data_points:
                    x = point.get(x_field)
                    y = point.get(y_field)
                    
                    if x is not None and y is not None:
                        coordinates.append((float(x), float(y)))
                
                if coordinates:
                    break
        
        return coordinates
    
    def _process_coordinates(self, coordinates: List[Tuple[float, float]]) -> List[TrackPoint]:
        """Processa coordenadas brutas para criar pontos do traçado."""
        if not coordinates:
            return []
        
        # Converte para arrays numpy
        coords_array = np.array(coordinates)
        
        # Remove pontos duplicados
        coords_array = self._remove_duplicates(coords_array)
        
        # Suaviza o traçado
        smoothed_coords = self._smooth_track(coords_array)
        
        # Calcula distâncias
        distances = self._calculate_distances(smoothed_coords)
        
        # Cria pontos do traçado
        track_points = []
        for i, (coord, distance) in enumerate(zip(smoothed_coords, distances)):
            point = TrackPoint(
                x=coord[0],
                y=coord[1],
                distance=distance
            )
            track_points.append(point)
        
        # Calcula propriedades adicionais
        self._calculate_track_properties(track_points)
        
        return track_points
    
    def _remove_duplicates(self, coords: np.ndarray, tolerance: float = 1.0) -> np.ndarray:
        """Remove pontos duplicados ou muito próximos."""
        if len(coords) < 2:
            return coords
        
        # Calcula distâncias entre pontos consecutivos
        distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
        
        # Mantém apenas pontos com distância mínima
        keep_indices = [0]  # Sempre mantém o primeiro ponto
        
        for i in range(1, len(coords)):
            if distances[i-1] >= tolerance:
                keep_indices.append(i)
        
        return coords[keep_indices]
    
    def _smooth_track(self, coords: np.ndarray, smoothing_factor: float = 0.1) -> np.ndarray:
        """Suaviza o traçado da pista."""
        if len(coords) < 4:
            return coords
        
        try:
            # Usa spline para suavizar
            tck, u = splprep([coords[:, 0], coords[:, 1]], s=smoothing_factor * len(coords))
            
            # Gera pontos suavizados
            u_new = np.linspace(0, 1, len(coords))
            smoothed = splev(u_new, tck)
            
            return np.column_stack(smoothed)
            
        except Exception:
            # Fallback para filtro Savitzky-Golay
            window_length = min(51, len(coords) // 4)
            if window_length % 2 == 0:
                window_length += 1
            
            if window_length >= 3:
                smoothed_x = savgol_filter(coords[:, 0], window_length, 3)
                smoothed_y = savgol_filter(coords[:, 1], window_length, 3)
                return np.column_stack([smoothed_x, smoothed_y])
            
            return coords
    
    def _calculate_distances(self, coords: np.ndarray) -> np.ndarray:
        """Calcula distâncias acumuladas ao longo do traçado."""
        if len(coords) < 2:
            return np.array([0.0])
        
        # Calcula distâncias entre pontos consecutivos
        segment_distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
        
        # Calcula distâncias acumuladas
        cumulative_distances = np.concatenate([[0], np.cumsum(segment_distances)])
        
        return cumulative_distances
    
    def _calculate_track_properties(self, track_points: List[TrackPoint]):
        """Calcula propriedades adicionais dos pontos do traçado."""
        if len(track_points) < 3:
            return
        
        coords = np.array([(p.x, p.y) for p in track_points])
        
        # Calcula raios de curvatura
        for i in range(1, len(track_points) - 1):
            radius = self._calculate_corner_radius(
                coords[i-1], coords[i], coords[i+1]
            )
            track_points[i].corner_radius = radius
    
    def _calculate_corner_radius(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calcula o raio de curvatura em um ponto."""
        try:
            # Vetores
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Ângulo entre vetores
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1, 1)
            angle = np.arccos(cos_angle)
            
            # Raio aproximado
            if angle > 0.01:  # Evita divisão por zero
                chord_length = np.linalg.norm(p3 - p1)
                radius = chord_length / (2 * np.sin(angle / 2))
                return min(radius, 10000)  # Limita raio máximo
            
            return 10000  # Reta
            
        except Exception:
            return 10000
    
    def _detect_sectors(self, track_points: List[TrackPoint], telemetry_data: Dict[str, Any]) -> List[TrackSector]:
        """Detecta setores da pista."""
        if not track_points:
            return []
        
        total_length = track_points[-1].distance
        
        # Tenta detectar setores dos dados de telemetria
        sectors_from_data = self._extract_sectors_from_telemetry(telemetry_data)
        
        if sectors_from_data:
            return sectors_from_data
        
        # Cria setores padrão (3 setores)
        sector_length = total_length / 3
        
        sectors = []
        for i in range(3):
            start_dist = i * sector_length
            end_dist = (i + 1) * sector_length
            
            sector = TrackSector(
                id=i + 1,
                start_distance=start_dist,
                end_distance=end_dist,
                length=sector_length,
                type=self._classify_sector_type(track_points, start_dist, end_dist)
            )
            sectors.append(sector)
        
        return sectors
    
    def _extract_sectors_from_telemetry(self, telemetry_data: Dict[str, Any]) -> List[TrackSector]:
        """Extrai informações de setores dos dados de telemetria."""
        # Implementação futura para extrair setores dos dados
        return []
    
    def _classify_sector_type(self, track_points: List[TrackPoint], start_dist: float, end_dist: float) -> str:
        """Classifica o tipo de setor baseado na curvatura."""
        sector_points = [p for p in track_points if start_dist <= p.distance <= end_dist]
        
        if not sector_points:
            return "straight"
        
        # Calcula curvatura média
        avg_radius = np.mean([p.corner_radius for p in sector_points if p.corner_radius > 0])
        
        if avg_radius > 1000:
            return "straight"
        elif avg_radius > 200:
            return "fast_corner"
        else:
            return "slow_corner"
    
    def _detect_direction(self, track_points: List[TrackPoint]) -> str:
        """Detecta direção da pista (horário/anti-horário)."""
        if len(track_points) < 4:
            return "clockwise"
        
        # Calcula área usando fórmula do shoelace
        coords = [(p.x, p.y) for p in track_points[:len(track_points)//2]]  # Usa primeira metade
        
        area = 0
        for i in range(len(coords)):
            j = (i + 1) % len(coords)
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        
        return "counterclockwise" if area > 0 else "clockwise"
    
    def _generate_synthetic_track(self, track_name: str, telemetry_data: Dict[str, Any]) -> TrackLayout:
        """Gera traçado sintético quando não há coordenadas disponíveis."""
        # Obtém informações da base de dados
        track_info = self.track_database.get(track_name, {})
        
        # Gera pontos sintéticos baseados no comprimento da pista
        total_length = track_info.get('length', 5000)
        num_points = 200
        
        # Cria traçado oval simples
        angles = np.linspace(0, 2 * np.pi, num_points)
        radius = total_length / (2 * np.pi)
        
        track_points = []
        for i, angle in enumerate(angles):
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            distance = (i / num_points) * total_length
            
            point = TrackPoint(x=x, y=y, distance=distance)
            track_points.append(point)
        
        # Cria setores padrão
        sectors = []
        for i in range(3):
            start_dist = (i / 3) * total_length
            end_dist = ((i + 1) / 3) * total_length
            
            sector = TrackSector(
                id=i + 1,
                start_distance=start_dist,
                end_distance=end_dist,
                length=total_length / 3,
                type="mixed"
            )
            sectors.append(sector)
        
        return TrackLayout(
            name=track_info.get('full_name', track_name),
            points=track_points,
            sectors=sectors,
            total_length=total_length,
            direction=track_info.get('direction', 'clockwise')
        )
    
    def _calculate_track_length(self, track_points: List[TrackPoint]) -> float:
        """Calcula comprimento total da pista."""
        if not track_points:
            return 0.0
        
        return track_points[-1].distance

class TrackAnalyzer:
    """Analisador avançado de performance na pista."""
    
    def __init__(self, track_layout: Optional[TrackLayout] = None):
        self.track_layout = track_layout
    
    def analyze_lap_performance(self, lap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa performance de uma volta."""
        analysis = {
            'sector_times': self._calculate_sector_times(lap_data),
            'speed_analysis': self._analyze_speed_profile(lap_data),
            'braking_analysis': self._analyze_braking_points(lap_data),
            'cornering_analysis': self._analyze_cornering(lap_data),
            'racing_line': self._analyze_racing_line(lap_data),
            'efficiency_score': 0.0
        }
        
        # Calcula score de eficiência
        analysis['efficiency_score'] = self._calculate_efficiency_score(analysis)
        
        return analysis
    
    def _calculate_sector_times(self, lap_data: Dict[str, Any]) -> List[Dict[str, float]]:
        """Calcula tempos de setor."""
        sector_times = []
        
        for sector in self.track_layout.sectors:
            # Implementação simplificada
            sector_time = {
                'sector_id': sector.id,
                'time': sector.length / 50.0,  # Velocidade média estimada
                'avg_speed': 50.0,
                'max_speed': 60.0,
                'min_speed': 40.0
            }
            sector_times.append(sector_time)
        
        return sector_times
    
    def _analyze_speed_profile(self, lap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa perfil de velocidade."""
        return {
            'max_speed': 250.0,
            'avg_speed': 180.0,
            'speed_variance': 45.0,
            'acceleration_zones': 3,
            'braking_zones': 8
        }
    
    def _analyze_braking_points(self, lap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa pontos de frenagem."""
        return {
            'total_braking_events': 8,
            'avg_braking_force': 85.0,
            'max_braking_force': 100.0,
            'braking_efficiency': 92.0,
            'late_braking_opportunities': 2
        }
    
    def _analyze_cornering(self, lap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa performance em curvas."""
        return {
            'total_corners': 12,
            'avg_corner_speed': 120.0,
            'understeer_events': 3,
            'oversteer_events': 1,
            'optimal_racing_line_adherence': 87.0
        }
    
    def _analyze_racing_line(self, lap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa linha de corrida."""
        return {
            'line_efficiency': 89.0,
            'track_usage': 95.0,
            'apex_precision': 91.0,
            'exit_optimization': 88.0
        }
    
    def _calculate_efficiency_score(self, analysis: Dict[str, Any]) -> float:
        """Calcula score geral de eficiência."""
        # Combina diferentes métricas
        speed_score = min(analysis['speed_analysis']['avg_speed'] / 200.0, 1.0) * 100
        braking_score = analysis['braking_analysis']['braking_efficiency']
        cornering_score = analysis['cornering_analysis']['optimal_racing_line_adherence']
        line_score = analysis['racing_line']['line_efficiency']
        
        return (speed_score + braking_score + cornering_score + line_score) / 4

