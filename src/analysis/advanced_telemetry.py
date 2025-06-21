"""
Sistema avançado de análise de telemetria que supera o MoTeC.
Implementa análises estatísticas, comparações e insights automáticos.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy import stats
from scipy.signal import find_peaks, butter, filtfilt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrica de performance."""
    name: str
    value: float
    unit: str
    category: str
    benchmark: Optional[float] = None
    percentile: Optional[float] = None
    trend: str = "stable"  # improving, declining, stable

@dataclass
class LapComparison:
    """Comparação entre voltas."""
    reference_lap: int
    comparison_lap: int
    time_delta: float
    sector_deltas: List[float]
    speed_delta_avg: float
    improvements: List[str]
    regressions: List[str]

@dataclass
class DriverInsight:
    """Insight automático sobre performance do piloto."""
    category: str
    title: str
    description: str
    severity: str  # info, warning, critical
    recommendation: str
    data_points: List[float]

class AdvancedTelemetryAnalyzer:
    """Analisador avançado de telemetria."""
    
    def __init__(self):
        self.analysis_cache = {}
        self.benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self) -> Dict[str, Dict]:
        """Carrega benchmarks de performance por pista."""
        return {
            "monza": {
                "lap_time": 80.0,
                "top_speed": 340.0,
                "avg_speed": 245.0,
                "braking_zones": 4,
                "acceleration_zones": 3
            },
            "spa": {
                "lap_time": 105.0,
                "top_speed": 320.0,
                "avg_speed": 220.0,
                "braking_zones": 8,
                "acceleration_zones": 6
            },
            "silverstone": {
                "lap_time": 88.0,
                "top_speed": 310.0,
                "avg_speed": 235.0,
                "braking_zones": 6,
                "acceleration_zones": 5
            }
        }
    
    def comprehensive_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise abrangente dos dados de telemetria."""
        try:
            analysis = {
                'session_overview': self._analyze_session_overview(telemetry_data),
                'lap_analysis': self._analyze_all_laps(telemetry_data),
                'performance_metrics': self._calculate_performance_metrics(telemetry_data),
                'driver_insights': self._generate_driver_insights(telemetry_data),
                'comparative_analysis': self._comparative_analysis(telemetry_data),
                'predictive_analysis': self._predictive_analysis(telemetry_data),
                'setup_recommendations': self._generate_setup_recommendations(telemetry_data),
                'consistency_analysis': self._analyze_consistency(telemetry_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise abrangente: {e}")
            return {}
    
    def _analyze_session_overview(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise geral da sessão."""
        laps = telemetry_data.get('laps', [])
        metadata = telemetry_data.get('metadata', {})
        
        if not laps:
            return {}
        
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        overview = {
            'total_laps': len(laps),
            'valid_laps': len(lap_times),
            'session_duration': metadata.get('duration', 0),
            'track': metadata.get('track', 'Unknown'),
            'car': metadata.get('car', 'Unknown'),
            'date': metadata.get('date', 'Unknown'),
            'weather_conditions': self._analyze_weather_conditions(telemetry_data),
            'session_type': self._detect_session_type(telemetry_data)
        }
        
        if lap_times:
            overview.update({
                'best_lap_time': min(lap_times),
                'worst_lap_time': max(lap_times),
                'average_lap_time': np.mean(lap_times),
                'lap_time_std': np.std(lap_times),
                'improvement_trend': self._calculate_improvement_trend(lap_times)
            })
        
        return overview
    
    def _analyze_all_laps(self, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Análise detalhada de todas as voltas."""
        laps = telemetry_data.get('laps', [])
        lap_analyses = []
        
        for i, lap in enumerate(laps):
            analysis = self._analyze_single_lap(lap, i + 1, telemetry_data)
            lap_analyses.append(analysis)
        
        return lap_analyses
    
    def _analyze_single_lap(self, lap_data: Dict[str, Any], lap_number: int, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise detalhada de uma volta específica."""
        data_points = lap_data.get('data_points', [])
        
        if not data_points:
            return {'lap_number': lap_number, 'valid': False}
        
        # Extrai dados dos canais
        channels_data = self._extract_channels_data(data_points)
        
        analysis = {
            'lap_number': lap_number,
            'lap_time': lap_data.get('lap_time', 0),
            'valid': True,
            'speed_analysis': self._analyze_speed_profile(channels_data),
            'throttle_analysis': self._analyze_throttle_usage(channels_data),
            'brake_analysis': self._analyze_braking_performance(channels_data),
            'steering_analysis': self._analyze_steering_input(channels_data),
            'g_force_analysis': self._analyze_g_forces(channels_data),
            'engine_analysis': self._analyze_engine_performance(channels_data),
            'tire_analysis': self._analyze_tire_performance(channels_data),
            'fuel_analysis': self._analyze_fuel_consumption(channels_data),
            'sector_analysis': self._analyze_sectors(lap_data, channels_data),
            'efficiency_metrics': self._calculate_efficiency_metrics(channels_data)
        }
        
        return analysis
    
    def _extract_channels_data(self, data_points: List[Dict]) -> Dict[str, List[float]]:
        """Extrai dados dos canais de telemetria."""
        channels = {}
        
        # Mapeia nomes de canais comuns
        channel_mapping = {
            'speed': ['SPEED', 'Speed', 'VEL', 'Velocity'],
            'throttle': ['THROTTLE', 'Throttle', 'TPS', 'ACCEL'],
            'brake': ['BRAKE', 'Brake', 'BRAKE_PRESS', 'BrakePressure'],
            'steering': ['STEERANGLE', 'SteerAngle', 'STEERING', 'Steering'],
            'g_lat': ['G_LAT', 'GLat', 'LATERAL_G', 'LateralG'],
            'g_long': ['G_LONG', 'GLong', 'LONGITUDINAL_G', 'LongitudinalG'],
            'rpm': ['RPM', 'Rpm', 'ENGINE_RPM', 'EngineRPM'],
            'gear': ['GEAR', 'Gear', 'CURRENT_GEAR'],
            'time': ['Time', 'TIME', 'Timestamp']
        }
        
        # Inicializa canais
        for channel_name in channel_mapping.keys():
            channels[channel_name] = []
        
        # Extrai dados
        for point in data_points:
            for channel_name, possible_names in channel_mapping.items():
                value = None
                for name in possible_names:
                    if name in point:
                        value = point[name]
                        break
                
                channels[channel_name].append(value if value is not None else 0.0)
        
        return channels
    
    def _analyze_speed_profile(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise do perfil de velocidade."""
        speed_data = channels_data.get('speed', [])
        
        if not speed_data or all(s == 0 for s in speed_data):
            return {'valid': False}
        
        speed_array = np.array([s for s in speed_data if s > 0])
        
        if len(speed_array) == 0:
            return {'valid': False}
        
        analysis = {
            'valid': True,
            'max_speed': float(np.max(speed_array)),
            'min_speed': float(np.min(speed_array)),
            'avg_speed': float(np.mean(speed_array)),
            'speed_variance': float(np.var(speed_array)),
            'speed_range': float(np.max(speed_array) - np.min(speed_array)),
            'acceleration_events': self._count_acceleration_events(speed_array),
            'deceleration_events': self._count_deceleration_events(speed_array),
            'top_speed_duration': self._calculate_top_speed_duration(speed_array),
            'speed_consistency': self._calculate_speed_consistency(speed_array)
        }
        
        return analysis
    
    def _analyze_throttle_usage(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise do uso do acelerador."""
        throttle_data = channels_data.get('throttle', [])
        
        if not throttle_data:
            return {'valid': False}
        
        throttle_array = np.array(throttle_data)
        
        analysis = {
            'valid': True,
            'full_throttle_percentage': float(np.sum(throttle_array >= 95) / len(throttle_array) * 100),
            'partial_throttle_percentage': float(np.sum((throttle_array > 10) & (throttle_array < 95)) / len(throttle_array) * 100),
            'off_throttle_percentage': float(np.sum(throttle_array <= 10) / len(throttle_array) * 100),
            'avg_throttle_position': float(np.mean(throttle_array)),
            'throttle_smoothness': self._calculate_input_smoothness(throttle_array),
            'throttle_application_rate': self._calculate_application_rate(throttle_array),
            'lift_and_coast_events': self._count_lift_and_coast(throttle_array)
        }
        
        return analysis
    
    def _analyze_braking_performance(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise da performance de frenagem."""
        brake_data = channels_data.get('brake', [])
        speed_data = channels_data.get('speed', [])
        
        if not brake_data:
            return {'valid': False}
        
        brake_array = np.array(brake_data)
        
        analysis = {
            'valid': True,
            'max_brake_pressure': float(np.max(brake_array)),
            'avg_brake_pressure': float(np.mean(brake_array[brake_array > 0])) if np.any(brake_array > 0) else 0.0,
            'braking_events': self._count_braking_events(brake_array),
            'brake_smoothness': self._calculate_input_smoothness(brake_array),
            'trail_braking_usage': self._analyze_trail_braking(brake_data, channels_data.get('steering', [])),
            'brake_balance': self._analyze_brake_balance(brake_array),
            'braking_efficiency': self._calculate_braking_efficiency(brake_data, speed_data)
        }
        
        return analysis
    
    def _analyze_steering_input(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise das entradas de direção."""
        steering_data = channels_data.get('steering', [])
        
        if not steering_data:
            return {'valid': False}
        
        steering_array = np.array(steering_data)
        
        analysis = {
            'valid': True,
            'max_steering_angle': float(np.max(np.abs(steering_array))),
            'avg_steering_input': float(np.mean(np.abs(steering_array))),
            'steering_smoothness': self._calculate_input_smoothness(steering_array),
            'steering_corrections': self._count_steering_corrections(steering_array),
            'lock_to_lock_time': self._calculate_lock_to_lock_time(steering_array),
            'understeer_indication': self._detect_understeer(steering_array, channels_data.get('g_lat', [])),
            'oversteer_indication': self._detect_oversteer(steering_array, channels_data.get('g_lat', []))
        }
        
        return analysis
    
    def _analyze_g_forces(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise das forças G."""
        g_lat_data = channels_data.get('g_lat', [])
        g_long_data = channels_data.get('g_long', [])
        
        if not g_lat_data and not g_long_data:
            return {'valid': False}
        
        analysis = {'valid': True}
        
        if g_lat_data:
            g_lat_array = np.array(g_lat_data)
            analysis.update({
                'max_lateral_g': float(np.max(np.abs(g_lat_array))),
                'avg_lateral_g': float(np.mean(np.abs(g_lat_array))),
                'lateral_g_consistency': self._calculate_g_consistency(g_lat_array)
            })
        
        if g_long_data:
            g_long_array = np.array(g_long_data)
            analysis.update({
                'max_longitudinal_g_accel': float(np.max(g_long_array)),
                'max_longitudinal_g_brake': float(np.abs(np.min(g_long_array))),
                'avg_longitudinal_g': float(np.mean(np.abs(g_long_array)))
            })
        
        return analysis
    
    def _analyze_engine_performance(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise da performance do motor."""
        rpm_data = channels_data.get('rpm', [])
        gear_data = channels_data.get('gear', [])
        
        if not rpm_data:
            return {'valid': False}
        
        rpm_array = np.array([r for r in rpm_data if r > 0])
        
        if len(rpm_array) == 0:
            return {'valid': False}
        
        analysis = {
            'valid': True,
            'max_rpm': float(np.max(rpm_array)),
            'avg_rpm': float(np.mean(rpm_array)),
            'rpm_variance': float(np.var(rpm_array)),
            'shift_points': self._analyze_shift_points(rpm_data, gear_data),
            'engine_efficiency': self._calculate_engine_efficiency(rpm_data, channels_data.get('throttle', [])),
            'rev_limit_hits': self._count_rev_limit_hits(rpm_array)
        }
        
        return analysis
    
    def _analyze_tire_performance(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise da performance dos pneus."""
        # Análise baseada em forças G e velocidade
        g_lat_data = channels_data.get('g_lat', [])
        speed_data = channels_data.get('speed', [])
        
        if not g_lat_data or not speed_data:
            return {'valid': False}
        
        analysis = {
            'valid': True,
            'grip_utilization': self._calculate_grip_utilization(g_lat_data, speed_data),
            'tire_slip_events': self._detect_tire_slip_events(g_lat_data),
            'cornering_performance': self._analyze_cornering_performance(g_lat_data, speed_data),
            'tire_degradation_indicator': self._estimate_tire_degradation(channels_data)
        }
        
        return analysis
    
    def _analyze_fuel_consumption(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise do consumo de combustível."""
        # Estimativa baseada em throttle e RPM
        throttle_data = channels_data.get('throttle', [])
        rpm_data = channels_data.get('rpm', [])
        time_data = channels_data.get('time', [])
        
        if not throttle_data or not rpm_data:
            return {'valid': False}
        
        # Cálculo estimado de consumo
        consumption_rate = self._estimate_fuel_consumption_rate(throttle_data, rpm_data)
        
        analysis = {
            'valid': True,
            'estimated_consumption_rate': consumption_rate,
            'fuel_efficiency_score': self._calculate_fuel_efficiency_score(throttle_data, rpm_data),
            'eco_driving_opportunities': self._identify_eco_driving_opportunities(throttle_data, rpm_data)
        }
        
        return analysis
    
    def _analyze_sectors(self, lap_data: Dict[str, Any], channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Análise por setores."""
        # Implementação simplificada - divide a volta em 3 setores
        total_points = len(channels_data.get('time', []))
        
        if total_points < 3:
            return {'valid': False}
        
        sector_size = total_points // 3
        sectors = []
        
        for i in range(3):
            start_idx = i * sector_size
            end_idx = (i + 1) * sector_size if i < 2 else total_points
            
            sector_data = {}
            for channel, data in channels_data.items():
                sector_data[channel] = data[start_idx:end_idx]
            
            sector_analysis = {
                'sector_number': i + 1,
                'speed_analysis': self._analyze_speed_profile(sector_data),
                'time_estimate': (end_idx - start_idx) * 0.05  # Estimativa baseada em 20Hz
            }
            
            sectors.append(sector_analysis)
        
        return {
            'valid': True,
            'sectors': sectors,
            'best_sector': min(range(3), key=lambda i: sectors[i]['time_estimate']),
            'sector_consistency': self._calculate_sector_consistency(sectors)
        }
    
    def _calculate_efficiency_metrics(self, channels_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calcula métricas de eficiência."""
        metrics = {
            'overall_efficiency': 0.0,
            'speed_efficiency': 0.0,
            'throttle_efficiency': 0.0,
            'brake_efficiency': 0.0,
            'steering_efficiency': 0.0
        }
        
        # Calcula eficiências individuais
        speed_data = channels_data.get('speed', [])
        if speed_data:
            metrics['speed_efficiency'] = self._calculate_speed_efficiency(speed_data)
        
        throttle_data = channels_data.get('throttle', [])
        if throttle_data:
            metrics['throttle_efficiency'] = self._calculate_throttle_efficiency(throttle_data)
        
        brake_data = channels_data.get('brake', [])
        if brake_data:
            metrics['brake_efficiency'] = self._calculate_brake_efficiency(brake_data)
        
        steering_data = channels_data.get('steering', [])
        if steering_data:
            metrics['steering_efficiency'] = self._calculate_steering_efficiency(steering_data)
        
        # Calcula eficiência geral
        efficiencies = [v for v in metrics.values() if v > 0]
        if efficiencies:
            metrics['overall_efficiency'] = np.mean(efficiencies)
        
        return metrics
    
    # Métodos auxiliares para cálculos específicos
    def _count_acceleration_events(self, speed_data: np.ndarray) -> int:
        """Conta eventos de aceleração."""
        if len(speed_data) < 2:
            return 0
        
        acceleration = np.diff(speed_data)
        peaks, _ = find_peaks(acceleration, height=2.0, distance=10)
        return len(peaks)
    
    def _count_deceleration_events(self, speed_data: np.ndarray) -> int:
        """Conta eventos de desaceleração."""
        if len(speed_data) < 2:
            return 0
        
        deceleration = -np.diff(speed_data)
        peaks, _ = find_peaks(deceleration, height=2.0, distance=10)
        return len(peaks)
    
    def _calculate_top_speed_duration(self, speed_data: np.ndarray) -> float:
        """Calcula duração em velocidade máxima."""
        if len(speed_data) == 0:
            return 0.0
        
        max_speed = np.max(speed_data)
        top_speed_threshold = max_speed * 0.95
        
        return float(np.sum(speed_data >= top_speed_threshold) / len(speed_data) * 100)
    
    def _calculate_speed_consistency(self, speed_data: np.ndarray) -> float:
        """Calcula consistência de velocidade."""
        if len(speed_data) == 0:
            return 0.0
        
        cv = np.std(speed_data) / np.mean(speed_data) if np.mean(speed_data) > 0 else 0
        return max(0, 100 - cv * 100)
    
    def _calculate_input_smoothness(self, input_data: np.ndarray) -> float:
        """Calcula suavidade de entrada."""
        if len(input_data) < 2:
            return 100.0
        
        # Calcula variação das derivadas
        derivatives = np.diff(input_data)
        smoothness = 100 - min(100, np.std(derivatives) * 10)
        
        return max(0, smoothness)
    
    def _calculate_application_rate(self, input_data: np.ndarray) -> float:
        """Calcula taxa de aplicação de entrada."""
        if len(input_data) < 2:
            return 0.0
        
        derivatives = np.diff(input_data)
        positive_derivatives = derivatives[derivatives > 0]
        
        return float(np.mean(positive_derivatives)) if len(positive_derivatives) > 0 else 0.0
    
    def _count_lift_and_coast(self, throttle_data: List[float]) -> int:
        """Conta eventos de lift and coast."""
        if len(throttle_data) < 10:
            return 0
        
        throttle_array = np.array(throttle_data)
        
        # Detecta reduções súbitas de throttle
        derivatives = np.diff(throttle_array)
        lift_events = np.where(derivatives < -20)[0]  # Redução de mais de 20%
        
        return len(lift_events)
    
    def _count_braking_events(self, brake_data: np.ndarray) -> int:
        """Conta eventos de frenagem."""
        if len(brake_data) < 2:
            return 0
        
        # Detecta início de frenagem
        brake_threshold = 10.0
        braking = brake_data > brake_threshold
        
        # Conta transições de não-frenagem para frenagem
        transitions = np.diff(braking.astype(int))
        return int(np.sum(transitions == 1))
    
    def _analyze_trail_braking(self, brake_data: List[float], steering_data: List[float]) -> float:
        """Analisa uso de trail braking."""
        if not brake_data or not steering_data:
            return 0.0
        
        brake_array = np.array(brake_data)
        steering_array = np.array(steering_data)
        
        # Detecta momentos com freio e direção simultâneos
        braking = brake_array > 10
        steering = np.abs(steering_array) > 5
        
        trail_braking_moments = np.sum(braking & steering)
        total_braking_moments = np.sum(braking)
        
        if total_braking_moments > 0:
            return float(trail_braking_moments / total_braking_moments * 100)
        
        return 0.0
    
    def _analyze_brake_balance(self, brake_data: np.ndarray) -> float:
        """Analisa equilíbrio de frenagem."""
        # Implementação simplificada
        if len(brake_data) == 0:
            return 50.0
        
        # Simula análise de equilíbrio baseada na consistência
        brake_variance = np.var(brake_data[brake_data > 0])
        balance_score = max(0, 100 - brake_variance)
        
        return float(balance_score)
    
    def _calculate_braking_efficiency(self, brake_data: List[float], speed_data: List[float]) -> float:
        """Calcula eficiência de frenagem."""
        if not brake_data or not speed_data:
            return 0.0
        
        # Implementação simplificada baseada na relação freio/desaceleração
        brake_array = np.array(brake_data)
        speed_array = np.array(speed_data)
        
        if len(speed_array) < 2:
            return 0.0
        
        deceleration = -np.diff(speed_array)
        braking_moments = brake_array[1:] > 10
        
        if np.sum(braking_moments) > 0:
            avg_deceleration = np.mean(deceleration[braking_moments])
            efficiency = min(100, avg_deceleration * 10)
            return max(0, efficiency)
        
        return 0.0
    
    def _count_steering_corrections(self, steering_data: np.ndarray) -> int:
        """Conta correções de direção."""
        if len(steering_data) < 3:
            return 0
        
        # Detecta mudanças de direção rápidas
        derivatives = np.diff(steering_data)
        sign_changes = np.diff(np.sign(derivatives))
        
        # Conta apenas mudanças significativas
        significant_changes = np.abs(sign_changes) > 1
        return int(np.sum(significant_changes))
    
    def _calculate_lock_to_lock_time(self, steering_data: np.ndarray) -> float:
        """Calcula tempo de lock-to-lock."""
        if len(steering_data) < 10:
            return 0.0
        
        # Encontra máximos e mínimos
        max_angle = np.max(steering_data)
        min_angle = np.min(steering_data)
        
        if max_angle - min_angle < 90:  # Menos de 90 graus de diferença
            return 0.0
        
        # Simula tempo baseado na variação
        return float(abs(max_angle - min_angle) / 180 * 2)  # Estimativa em segundos
    
    def _detect_understeer(self, steering_data: np.ndarray, g_lat_data: List[float]) -> float:
        """Detecta indicações de understeer."""
        if not g_lat_data or len(steering_data) == 0:
            return 0.0
        
        # Implementação simplificada
        steering_input = np.abs(steering_data)
        g_lat_array = np.array(g_lat_data)
        
        if len(g_lat_array) != len(steering_input):
            return 0.0
        
        # Detecta momentos com muito steering mas pouco G lateral
        high_steering = steering_input > np.percentile(steering_input, 75)
        low_g_lat = np.abs(g_lat_array) < np.percentile(np.abs(g_lat_array), 50)
        
        understeer_moments = np.sum(high_steering & low_g_lat)
        total_steering_moments = np.sum(high_steering)
        
        if total_steering_moments > 0:
            return float(understeer_moments / total_steering_moments * 100)
        
        return 0.0
    
    def _detect_oversteer(self, steering_data: np.ndarray, g_lat_data: List[float]) -> float:
        """Detecta indicações de oversteer."""
        if not g_lat_data or len(steering_data) == 0:
            return 0.0
        
        # Detecta correções rápidas de direção
        corrections = self._count_steering_corrections(steering_data)
        total_time = len(steering_data) * 0.05  # Assumindo 20Hz
        
        if total_time > 0:
            return float(corrections / total_time * 60)  # Correções por minuto
        
        return 0.0
    
    def _calculate_g_consistency(self, g_data: np.ndarray) -> float:
        """Calcula consistência das forças G."""
        if len(g_data) == 0:
            return 0.0
        
        cv = np.std(g_data) / np.mean(np.abs(g_data)) if np.mean(np.abs(g_data)) > 0 else 0
        return max(0, 100 - cv * 50)
    
    def _analyze_shift_points(self, rpm_data: List[float], gear_data: List[float]) -> Dict[str, Any]:
        """Analisa pontos de troca de marcha."""
        if not rpm_data or not gear_data:
            return {'shift_count': 0, 'avg_shift_rpm': 0}
        
        gear_array = np.array(gear_data)
        rpm_array = np.array(rpm_data)
        
        # Detecta mudanças de marcha
        gear_changes = np.diff(gear_array)
        upshift_indices = np.where(gear_changes > 0)[0]
        
        if len(upshift_indices) > 0:
            shift_rpms = rpm_array[upshift_indices]
            return {
                'shift_count': len(upshift_indices),
                'avg_shift_rpm': float(np.mean(shift_rpms)),
                'optimal_shift_rpm': 7500.0  # Valor padrão
            }
        
        return {'shift_count': 0, 'avg_shift_rpm': 0}
    
    def _calculate_engine_efficiency(self, rpm_data: List[float], throttle_data: List[float]) -> float:
        """Calcula eficiência do motor."""
        if not rpm_data or not throttle_data:
            return 0.0
        
        rpm_array = np.array(rpm_data)
        throttle_array = np.array(throttle_data)
        
        # Calcula eficiência baseada na relação RPM/throttle
        efficiency_points = []
        
        for rpm, throttle in zip(rpm_array, throttle_array):
            if throttle > 10 and rpm > 1000:
                # Eficiência maior em RPMs médios com throttle moderado
                optimal_rpm = 6000
                rpm_efficiency = 1 - abs(rpm - optimal_rpm) / optimal_rpm
                throttle_efficiency = throttle / 100
                
                efficiency = (rpm_efficiency + throttle_efficiency) / 2
                efficiency_points.append(efficiency)
        
        return float(np.mean(efficiency_points) * 100) if efficiency_points else 0.0
    
    def _count_rev_limit_hits(self, rpm_data: np.ndarray) -> int:
        """Conta toques no limitador."""
        if len(rpm_data) == 0:
            return 0
        
        rev_limit = 8000  # RPM limite padrão
        return int(np.sum(rpm_data >= rev_limit))
    
    # Métodos para análises específicas de pneus e combustível
    def _calculate_grip_utilization(self, g_lat_data: List[float], speed_data: List[float]) -> float:
        """Calcula utilização do grip dos pneus."""
        if not g_lat_data or not speed_data:
            return 0.0
        
        g_lat_array = np.array(g_lat_data)
        max_g_lat = np.max(np.abs(g_lat_array))
        
        # Estima grip máximo baseado na velocidade
        theoretical_max_g = 1.5  # G lateral máximo teórico
        
        if theoretical_max_g > 0:
            return float(min(100, max_g_lat / theoretical_max_g * 100))
        
        return 0.0
    
    def _detect_tire_slip_events(self, g_lat_data: List[float]) -> int:
        """Detecta eventos de deslizamento dos pneus."""
        if not g_lat_data:
            return 0
        
        g_lat_array = np.array(g_lat_data)
        
        # Detecta variações súbitas nas forças G laterais
        if len(g_lat_array) < 2:
            return 0
        
        g_lat_changes = np.abs(np.diff(g_lat_array))
        slip_threshold = 0.3  # Mudança súbita de 0.3G
        
        slip_events = np.sum(g_lat_changes > slip_threshold)
        return int(slip_events)
    
    def _analyze_cornering_performance(self, g_lat_data: List[float], speed_data: List[float]) -> Dict[str, float]:
        """Analisa performance em curvas."""
        if not g_lat_data or not speed_data:
            return {'cornering_speed': 0.0, 'cornering_g': 0.0}
        
        g_lat_array = np.array(g_lat_data)
        speed_array = np.array(speed_data)
        
        # Identifica momentos de curva (G lateral > 0.5)
        cornering_moments = np.abs(g_lat_array) > 0.5
        
        if np.sum(cornering_moments) > 0:
            avg_cornering_speed = np.mean(speed_array[cornering_moments])
            avg_cornering_g = np.mean(np.abs(g_lat_array[cornering_moments]))
            
            return {
                'cornering_speed': float(avg_cornering_speed),
                'cornering_g': float(avg_cornering_g)
            }
        
        return {'cornering_speed': 0.0, 'cornering_g': 0.0}
    
    def _estimate_tire_degradation(self, channels_data: Dict[str, List[float]]) -> float:
        """Estima degradação dos pneus."""
        # Implementação simplificada baseada na consistência das forças G
        g_lat_data = channels_data.get('g_lat', [])
        
        if not g_lat_data:
            return 0.0
        
        g_lat_array = np.array(g_lat_data)
        
        # Calcula variabilidade como indicador de degradação
        if len(g_lat_array) > 10:
            first_half = g_lat_array[:len(g_lat_array)//2]
            second_half = g_lat_array[len(g_lat_array)//2:]
            
            first_half_std = np.std(first_half)
            second_half_std = np.std(second_half)
            
            if first_half_std > 0:
                degradation = (second_half_std - first_half_std) / first_half_std * 100
                return max(0, min(100, degradation))
        
        return 0.0
    
    def _estimate_fuel_consumption_rate(self, throttle_data: List[float], rpm_data: List[float]) -> float:
        """Estima taxa de consumo de combustível."""
        if not throttle_data or not rpm_data:
            return 0.0
        
        throttle_array = np.array(throttle_data)
        rpm_array = np.array(rpm_data)
        
        # Fórmula simplificada: consumo baseado em throttle e RPM
        consumption_factors = (throttle_array / 100) * (rpm_array / 8000)
        avg_consumption_factor = np.mean(consumption_factors)
        
        # Converte para litros por 100km (estimativa)
        base_consumption = 25.0  # L/100km base
        return float(base_consumption * (1 + avg_consumption_factor))
    
    def _calculate_fuel_efficiency_score(self, throttle_data: List[float], rpm_data: List[float]) -> float:
        """Calcula score de eficiência de combustível."""
        if not throttle_data or not rpm_data:
            return 0.0
        
        throttle_array = np.array(throttle_data)
        rpm_array = np.array(rpm_data)
        
        # Penaliza throttle alto e RPM alto
        efficiency_penalties = (throttle_array / 100) * 0.5 + (rpm_array / 8000) * 0.3
        avg_penalty = np.mean(efficiency_penalties)
        
        efficiency_score = max(0, 100 - avg_penalty * 100)
        return float(efficiency_score)
    
    def _identify_eco_driving_opportunities(self, throttle_data: List[float], rpm_data: List[float]) -> List[str]:
        """Identifica oportunidades de eco-driving."""
        opportunities = []
        
        if not throttle_data or not rpm_data:
            return opportunities
        
        throttle_array = np.array(throttle_data)
        rpm_array = np.array(rpm_data)
        
        # Verifica uso excessivo de throttle
        high_throttle_percentage = np.sum(throttle_array > 80) / len(throttle_array) * 100
        if high_throttle_percentage > 30:
            opportunities.append("Reduzir uso de throttle alto")
        
        # Verifica RPM alto
        high_rpm_percentage = np.sum(rpm_array > 7000) / len(rpm_array) * 100
        if high_rpm_percentage > 20:
            opportunities.append("Trocar marchas mais cedo")
        
        # Verifica suavidade
        throttle_smoothness = self._calculate_input_smoothness(throttle_array)
        if throttle_smoothness < 70:
            opportunities.append("Aplicar throttle mais suavemente")
        
        return opportunities
    
    # Métodos para cálculos de eficiência
    def _calculate_speed_efficiency(self, speed_data: List[float]) -> float:
        """Calcula eficiência de velocidade."""
        if not speed_data:
            return 0.0
        
        speed_array = np.array(speed_data)
        
        # Eficiência baseada na manutenção de velocidade alta
        avg_speed = np.mean(speed_array)
        max_speed = np.max(speed_array)
        
        if max_speed > 0:
            return float(avg_speed / max_speed * 100)
        
        return 0.0
    
    def _calculate_throttle_efficiency(self, throttle_data: List[float]) -> float:
        """Calcula eficiência do throttle."""
        if not throttle_data:
            return 0.0
        
        throttle_array = np.array(throttle_data)
        
        # Eficiência baseada na suavidade e uso otimizado
        smoothness = self._calculate_input_smoothness(throttle_array)
        
        # Penaliza uso excessivo de throttle baixo
        low_throttle_penalty = np.sum(throttle_array < 20) / len(throttle_array) * 20
        
        efficiency = smoothness - low_throttle_penalty
        return max(0, efficiency)
    
    def _calculate_brake_efficiency(self, brake_data: List[float]) -> float:
        """Calcula eficiência de frenagem."""
        if not brake_data:
            return 0.0
        
        brake_array = np.array(brake_data)
        
        # Eficiência baseada na suavidade e uso mínimo
        smoothness = self._calculate_input_smoothness(brake_array)
        
        # Premia uso mínimo de freio
        brake_usage = np.sum(brake_array > 10) / len(brake_array) * 100
        usage_efficiency = max(0, 100 - brake_usage)
        
        return float((smoothness + usage_efficiency) / 2)
    
    def _calculate_steering_efficiency(self, steering_data: List[float]) -> float:
        """Calcula eficiência de direção."""
        if not steering_data:
            return 0.0
        
        steering_array = np.array(steering_data)
        
        # Eficiência baseada na suavidade e correções mínimas
        smoothness = self._calculate_input_smoothness(steering_array)
        corrections = self._count_steering_corrections(steering_array)
        
        # Penaliza muitas correções
        correction_penalty = min(50, corrections * 2)
        
        efficiency = smoothness - correction_penalty
        return max(0, efficiency)
    
    def _calculate_sector_consistency(self, sectors: List[Dict]) -> float:
        """Calcula consistência entre setores."""
        if len(sectors) < 2:
            return 100.0
        
        sector_times = [s.get('time_estimate', 0) for s in sectors]
        
        if all(t == 0 for t in sector_times):
            return 100.0
        
        cv = np.std(sector_times) / np.mean(sector_times) if np.mean(sector_times) > 0 else 0
        consistency = max(0, 100 - cv * 100)
        
        return float(consistency)
    
    # Métodos para análises de sessão e insights
    def _analyze_weather_conditions(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa condições climáticas."""
        # Implementação simplificada - normalmente viria dos dados
        return {
            'temperature': 'Unknown',
            'humidity': 'Unknown',
            'wind': 'Unknown',
            'track_condition': 'Dry'  # Assumindo pista seca
        }
    
    def _detect_session_type(self, telemetry_data: Dict[str, Any]) -> str:
        """Detecta tipo de sessão."""
        laps = telemetry_data.get('laps', [])
        
        if len(laps) <= 3:
            return 'Qualifying'
        elif len(laps) <= 10:
            return 'Practice'
        else:
            return 'Race'
    
    def _calculate_improvement_trend(self, lap_times: List[float]) -> str:
        """Calcula tendência de melhoria."""
        if len(lap_times) < 3:
            return 'Insufficient data'
        
        # Calcula tendência linear
        x = np.arange(len(lap_times))
        slope, _, r_value, _, _ = stats.linregress(x, lap_times)
        
        if abs(r_value) < 0.3:
            return 'Stable'
        elif slope < 0:
            return 'Improving'
        else:
            return 'Declining'
    
    def _calculate_performance_metrics(self, telemetry_data: Dict[str, Any]) -> List[PerformanceMetric]:
        """Calcula métricas de performance."""
        metrics = []
        
        laps = telemetry_data.get('laps', [])
        if not laps:
            return metrics
        
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if lap_times:
            # Melhor volta
            best_lap = min(lap_times)
            metrics.append(PerformanceMetric(
                name='Best Lap Time',
                value=best_lap,
                unit='seconds',
                category='Lap Times'
            ))
            
            # Consistência
            consistency = (1 - np.std(lap_times) / np.mean(lap_times)) * 100 if np.mean(lap_times) > 0 else 0
            metrics.append(PerformanceMetric(
                name='Lap Time Consistency',
                value=consistency,
                unit='%',
                category='Consistency'
            ))
        
        return metrics
    
    def _generate_driver_insights(self, telemetry_data: Dict[str, Any]) -> List[DriverInsight]:
        """Gera insights automáticos sobre o piloto."""
        insights = []
        
        laps = telemetry_data.get('laps', [])
        if not laps:
            return insights
        
        # Análise de consistência
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if len(lap_times) >= 3:
            consistency = (1 - np.std(lap_times) / np.mean(lap_times)) * 100 if np.mean(lap_times) > 0 else 0
            
            if consistency < 95:
                insights.append(DriverInsight(
                    category='Consistency',
                    title='Inconsistência nos tempos de volta',
                    description=f'Variação de {np.std(lap_times):.2f}s entre voltas',
                    severity='warning',
                    recommendation='Foque na repetibilidade e suavidade dos inputs',
                    data_points=lap_times
                ))
            
            # Análise de melhoria
            if len(lap_times) >= 5:
                first_half = lap_times[:len(lap_times)//2]
                second_half = lap_times[len(lap_times)//2:]
                
                improvement = np.mean(first_half) - np.mean(second_half)
                
                if improvement > 0.5:
                    insights.append(DriverInsight(
                        category='Progress',
                        title='Melhoria significativa durante a sessão',
                        description=f'Melhoria de {improvement:.2f}s entre primeira e segunda metade',
                        severity='info',
                        recommendation='Continue com a abordagem atual',
                        data_points=lap_times
                    ))
        
        return insights
    
    def _comparative_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise comparativa entre voltas."""
        laps = telemetry_data.get('laps', [])
        
        if len(laps) < 2:
            return {'comparisons': []}
        
        comparisons = []
        
        # Compara melhor volta com volta média
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if lap_times:
            best_lap_idx = lap_times.index(min(lap_times))
            avg_lap_time = np.mean(lap_times)
            
            comparison = LapComparison(
                reference_lap=best_lap_idx + 1,
                comparison_lap=0,  # Volta média
                time_delta=avg_lap_time - min(lap_times),
                sector_deltas=[0.0, 0.0, 0.0],  # Simplificado
                speed_delta_avg=0.0,
                improvements=['Melhor volta identificada'],
                regressions=['Inconsistência em outras voltas']
            )
            
            comparisons.append(comparison)
        
        return {'comparisons': comparisons}
    
    def _predictive_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise preditiva."""
        laps = telemetry_data.get('laps', [])
        
        if len(laps) < 3:
            return {'predictions': []}
        
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        predictions = []
        
        if len(lap_times) >= 3:
            # Prediz próximo tempo de volta baseado na tendência
            x = np.arange(len(lap_times))
            slope, intercept, _, _, _ = stats.linregress(x, lap_times)
            
            next_lap_prediction = slope * len(lap_times) + intercept
            
            predictions.append({
                'type': 'Next Lap Time',
                'value': next_lap_prediction,
                'confidence': 0.7,
                'description': 'Baseado na tendência atual'
            })
        
        return {'predictions': predictions}
    
    def _generate_setup_recommendations(self, telemetry_data: Dict[str, Any]) -> List[str]:
        """Gera recomendações de setup."""
        recommendations = []
        
        # Análise simplificada baseada nos dados disponíveis
        laps = telemetry_data.get('laps', [])
        
        if not laps:
            return recommendations
        
        # Analisa primeira volta com dados detalhados
        first_lap = laps[0] if laps else {}
        data_points = first_lap.get('data_points', [])
        
        if data_points:
            # Verifica se há dados de velocidade
            speeds = [p.get('SPEED', 0) for p in data_points if p.get('SPEED', 0) > 0]
            
            if speeds:
                max_speed = max(speeds)
                
                if max_speed < 200:
                    recommendations.append("Considere reduzir downforce para maior velocidade máxima")
                elif max_speed > 300:
                    recommendations.append("Considere aumentar downforce para melhor estabilidade")
        
        # Recomendações baseadas em consistência
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if len(lap_times) >= 3:
            consistency = (1 - np.std(lap_times) / np.mean(lap_times)) * 100 if np.mean(lap_times) > 0 else 0
            
            if consistency < 95:
                recommendations.append("Ajuste o setup para melhor previsibilidade do carro")
        
        return recommendations
    
    def _analyze_consistency(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise de consistência."""
        laps = telemetry_data.get('laps', [])
        
        if len(laps) < 3:
            return {'overall_consistency': 0.0}
        
        lap_times = [lap.get('lap_time', 0) for lap in laps if lap.get('lap_time', 0) > 0]
        
        if not lap_times:
            return {'overall_consistency': 0.0}
        
        # Calcula métricas de consistência
        mean_time = np.mean(lap_times)
        std_time = np.std(lap_times)
        cv = std_time / mean_time if mean_time > 0 else 0
        
        consistency_score = max(0, 100 - cv * 100)
        
        # Analisa tendências
        x = np.arange(len(lap_times))
        slope, _, r_value, _, _ = stats.linregress(x, lap_times)
        
        return {
            'overall_consistency': consistency_score,
            'lap_time_variance': std_time,
            'coefficient_of_variation': cv,
            'trend_strength': abs(r_value),
            'improvement_rate': -slope if slope < 0 else 0,
            'degradation_rate': slope if slope > 0 else 0
        }



    def _smooth_data(self, data: List[float], window_size: int = 5) -> List[float]:
        """Aplica um filtro de média móvel para suavizar os dados."""
        if not data or len(data) < window_size:
            return data
        
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid').tolist()

    def _butter_lowpass_filter(self, data: List[float], cutoff: float, fs: float, order: int = 5) -> List[float]:
        """Aplica um filtro Butterworth passa-baixa nos dados."""
        nyq = 0.5 * fs  # Frequência de Nyquist
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y.tolist()

    def _detect_peaks(self, data: List[float], height: float = None, distance: int = None) -> List[int]:
        """Detecta picos em uma série de dados."""
        peaks, _ = find_peaks(data, height=height, distance=distance)
        return peaks.tolist()

    def _detect_valleys(self, data: List[float], height: float = None, distance: int = None) -> List[int]:
        """Detecta vales em uma série de dados (picos invertidos)."""
        valleys, _ = find_peaks([-x for x in data], height=height, distance=distance)
        return valleys.tolist()

    def _calculate_input_smoothness(self, input_data: np.ndarray) -> float:
        """Calcula a suavidade de uma entrada (acelerador, freio, direção)."""
        if len(input_data) < 2:
            return 100.0  # Perfeitamente suave se não houver movimento
        
        # Variação total
        total_variation = np.sum(np.abs(np.diff(input_data)))
        
        # Normaliza pela amplitude máxima possível da entrada (0-100 para %)
        # ou pela amplitude real dos dados se for um ângulo de direção
        max_amplitude = np.max(input_data) - np.min(input_data)
        if max_amplitude == 0:
            return 100.0
        
        # Quanto menor a variação em relação à amplitude, mais suave
        smoothness = 100.0 - (total_variation / (len(input_data) * max_amplitude)) * 100.0
        return max(0.0, min(100.0, smoothness))

    def _calculate_application_rate(self, input_data: np.ndarray, sample_rate: float = 60.0) -> float:
        """Calcula a taxa média de aplicação/liberação de uma entrada."""
        if len(input_data) < 2:
            return 0.0
        
        diffs = np.abs(np.diff(input_data))
        return np.mean(diffs) * sample_rate

    def _count_lift_and_coast(self, throttle_data: np.ndarray, speed_data: np.ndarray = None, threshold_throttle: float = 5.0, threshold_speed_drop: float = 5.0) -> int:
        """Conta eventos de 'lift and coast' (tirar o pé do acelerador e manter velocidade)."""
        if len(throttle_data) < 2:
            return 0
        
        lift_and_coast_events = 0
        in_lift_and_coast = False
        
        for i in range(1, len(throttle_data)):
            # Detecta 


            if throttle_data[i] < threshold_throttle and throttle_data[i-1] >= threshold_throttle:
                in_lift_and_coast = True
            
            # Detecta fim do lift and coast (acelerador de volta ou freio)
            if in_lift_and_coast and (throttle_data[i] >= threshold_throttle or (speed_data is not None and speed_data[i] < speed_data[i-1] - threshold_speed_drop)):
                lift_and_coast_events += 1
                in_lift_and_coast = False
                
        return lift_and_coast_events

    def _count_acceleration_events(self, speed_data: np.ndarray, threshold: float = 5.0) -> int:
        """Conta eventos de aceleração significativa."""
        if len(speed_data) < 2:
            return 0
        
        speed_diff = np.diff(speed_data)
        peaks, _ = find_peaks(speed_diff, height=threshold)
        return len(peaks)

    def _count_deceleration_events(self, speed_data: np.ndarray, threshold: float = 5.0) -> int:
        """Conta eventos de desaceleração significativa."""
        if len(speed_data) < 2:
            return 0
        
        speed_diff = np.diff(speed_data)
        peaks, _ = find_peaks(-speed_diff, height=threshold) # Picos negativos
        return len(peaks)

    def _calculate_top_speed_duration(self, speed_data: np.ndarray, top_speed_threshold_percent: float = 0.95) -> float:
        """Calcula a duração em que o carro está próximo da velocidade máxima."""
        if len(speed_data) == 0:
            return 0.0
        
        max_speed = np.max(speed_data)
        if max_speed == 0:
            return 0.0
            
        threshold_speed = max_speed * top_speed_threshold_percent
        
        duration = np.sum(speed_data >= threshold_speed) / 60.0 # Assumindo 60Hz de amostragem
        return duration

    def _calculate_speed_consistency(self, speed_data: np.ndarray) -> float:
        """Calcula a consistência da velocidade (baixa variação)."""
        if len(speed_data) < 2:
            return 100.0
        
        # Usa coeficiente de variação (desvio padrão / média)
        mean_speed = np.mean(speed_data)
        std_speed = np.std(speed_data)
        
        if mean_speed == 0:
            return 0.0
            
        cv = (std_speed / mean_speed) * 100
        return max(0.0, 100.0 - cv) # Quanto menor o CV, maior a consistência

    def _count_braking_events(self, brake_data: np.ndarray, threshold: float = 10.0) -> int:
        """Conta eventos de frenagem significativa."""
        if len(brake_data) < 2:
            return 0
        
        # Detecta quando o freio é aplicado acima de um limiar
        braking_events = 0
        is_braking = False
        for val in brake_data:
            if val >= threshold and not is_braking:
                braking_events += 1
                is_braking = True
            elif val < threshold and is_braking:
                is_braking = False
        return braking_events

    def _analyze_trail_braking(self, brake_data: List[float], steering_data: List[float], brake_threshold: float = 5.0, steering_threshold: float = 5.0) -> float:
        """Analisa o uso de trail braking (freio e direção simultaneamente)."""
        if len(brake_data) != len(steering_data) or len(brake_data) == 0:
            return 0.0
        
        trail_braking_duration = 0
        for i in range(len(brake_data)):
            if brake_data[i] > brake_threshold and abs(steering_data[i]) > steering_threshold:
                trail_braking_duration += 1
                
        return trail_braking_duration / 60.0 # Duração em segundos (assumindo 60Hz)

    def _analyze_brake_balance(self, brake_data: np.ndarray) -> Dict[str, float]:
        """Analisa o balanço de frenagem (requer dados de freio dianteiro/traseiro, aqui simulado)."""
        # Placeholder: Em um sistema real, precisaria de canais como BrakePressureFL, BrakePressureFR, etc.
        # Aqui, apenas uma simulação.
        
        # Simula uma distribuição para front/rear
        front_bias = 0.6 # Ex: 60% na frente
        rear_bias = 0.4 # Ex: 40% atrás
        
        total_brake_input = np.sum(brake_data)
        
        if total_brake_input == 0:
            return {"front_bias": 0.0, "rear_bias": 0.0, "optimal": True}
            
        # Simula variação
        simulated_front_brake = total_brake_input * front_bias * (1 + np.random.normal(0, 0.05))
        simulated_rear_brake = total_brake_input * rear_bias * (1 + np.random.normal(0, 0.05))
        
        total_simulated = simulated_front_brake + simulated_rear_brake
        
        if total_simulated == 0:
            return {"front_bias": 0.0, "rear_bias": 0.0, "optimal": True}
            
        actual_front_bias = simulated_front_brake / total_simulated
        actual_rear_bias = simulated_rear_brake / total_simulated
        
        # Verifica se está próximo do ideal (ex: 60/40)
        optimal = abs(actual_front_bias - 0.6) < 0.05
        
        return {"front_bias": actual_front_bias, "rear_bias": actual_rear_bias, "optimal": optimal}

    def _calculate_braking_efficiency(self, brake_data: np.ndarray, speed_data: np.ndarray) -> float:
        """Calcula a eficiência de frenagem (quanto de velocidade é perdida por unidade de freio)."""
        if len(brake_data) < 2 or len(speed_data) < 2:
            return 0.0
        
        # Identifica zonas de frenagem
        braking_zones_efficiency = []
        in_braking_zone = False
        start_speed = 0.0
        end_speed = 0.0
        total_brake_applied = 0.0
        
        for i in range(1, len(brake_data)):
            if brake_data[i] > 5 and not in_braking_zone: # Início da frenagem
                in_braking_zone = True
                start_speed = speed_data[i-1]
                total_brake_applied = brake_data[i]
            elif brake_data[i] > 5 and in_braking_zone: # Durante a frenagem
                total_brake_applied += brake_data[i]
            elif brake_data[i] <= 5 and in_braking_zone: # Fim da frenagem
                in_braking_zone = False
                end_speed = speed_data[i]
                
                speed_loss = start_speed - end_speed
                if speed_loss > 0 and total_brake_applied > 0:
                    efficiency = speed_loss / total_brake_applied
                    braking_zones_efficiency.append(efficiency)
                    
        if not braking_zones_efficiency:
            return 0.0
            
        return float(np.mean(braking_zones_efficiency))

    def _count_steering_corrections(self, steering_data: np.ndarray, threshold: float = 2.0) -> int:
        """Conta o número de correções de direção (pequenas mudanças rápidas)."""
        if len(steering_data) < 2:
            return 0
        
        corrections = 0
        for i in range(1, len(steering_data)):
            if abs(steering_data[i] - steering_data[i-1]) > threshold:
                corrections += 1
        return corrections

    def _calculate_lock_to_lock_time(self, steering_data: np.ndarray, sample_rate: float = 60.0) -> float:
        """Calcula o tempo para ir de um extremo ao outro da direção (lock-to-lock)."""
        if len(steering_data) < 10:
            return 0.0
        
        # Encontra os ângulos máximos e mínimos
        max_angle = np.max(steering_data)
        min_angle = np.min(steering_data)
        
        if abs(max_angle - min_angle) < 10: # Não houve movimento suficiente
            return 0.0
            
        # Encontra transições de um extremo ao outro
        lock_to_lock_times = []
        
        # Simplificado: procura por grandes mudanças de sinal
        for i in range(1, len(steering_data)):
            if (steering_data[i-1] < 0 and steering_data[i] > 0 and abs(steering_data[i] - steering_data[i-1]) > 50) or \
               (steering_data[i-1] > 0 and steering_data[i] < 0 and abs(steering_data[i] - steering_data[i-1]) > 50):
                # Isso é uma simplificação. O ideal seria detectar o ponto exato de 


                # inversão e calcular o tempo entre eles.
                lock_to_lock_times.append(1 / sample_rate) # Simplificado
        
        if lock_to_lock_times:
            return float(np.mean(lock_to_lock_times))
        return 0.0

    def _detect_understeer(self, steering_data: np.ndarray, g_lat_data: np.ndarray, threshold_steering: float = 10.0, threshold_g_lat: float = 0.5) -> float:
        """Detecta indicação de subesterço (muita direção para pouca força G lateral)."""
        if len(steering_data) != len(g_lat_data) or len(steering_data) == 0:
            return 0.0
        
        understeer_duration = 0
        for i in range(len(steering_data)):
            if abs(steering_data[i]) > threshold_steering and abs(g_lat_data[i]) < threshold_g_lat:
                understeer_duration += 1
                
        return understeer_duration / 60.0 # Duração em segundos

    def _detect_oversteer(self, steering_data: np.ndarray, g_lat_data: np.ndarray, threshold_steering_rate: float = 5.0, threshold_g_lat_change: float = 0.2) -> float:
        """Detecta indicação de sobreesterço (correções rápidas de direção com mudança de força G lateral)."""
        if len(steering_data) < 2 or len(g_lat_data) < 2:
            return 0.0
        
        oversteer_duration = 0
        for i in range(1, len(steering_data)):
            # Grande mudança na direção e na força G lateral
            if abs(steering_data[i] - steering_data[i-1]) > threshold_steering_rate and \
               abs(g_lat_data[i] - g_lat_data[i-1]) > threshold_g_lat_change:
                oversteer_duration += 1
                
        return oversteer_duration / 60.0 # Duração em segundos

    def _calculate_g_consistency(self, g_data: np.ndarray) -> float:
        """Calcula a consistência das forças G (baixa variação)."""
        if len(g_data) < 2:
            return 100.0
        
        mean_g = np.mean(np.abs(g_data))
        std_g = np.std(np.abs(g_data))
        
        if mean_g == 0:
            return 0.0
            
        cv = (std_g / mean_g) * 100
        return max(0.0, 100.0 - cv)

    def _analyze_shift_points(self, rpm_data: List[float], gear_data: List[int]) -> Dict[str, Any]:
        """Analisa os pontos de troca de marcha."""
        shift_points = {
            "upshifts": [],
            "downshifts": []
        }
        
        if len(rpm_data) != len(gear_data) or len(gear_data) < 2:
            return shift_points
            
        for i in range(1, len(gear_data)):
            if gear_data[i] > gear_data[i-1]: # Upshift
                shift_points["upshifts"].append({"index": i, "rpm": rpm_data[i-1]})
            elif gear_data[i] < gear_data[i-1]: # Downshift
                shift_points["downshifts"].append({"index": i, "rpm": rpm_data[i-1]})
                
        return shift_points

    def _calculate_engine_efficiency(self, rpm_data: np.ndarray, throttle_data: np.ndarray) -> float:
        """Calcula uma métrica de eficiência do motor (RPM vs. Acelerador)."""
        if len(rpm_data) != len(throttle_data) or len(rpm_data) == 0:
            return 0.0
        
        # Penaliza RPMs muito altos com pouco acelerador ou vice-versa
        efficiency_score = 0.0
        for i in range(len(rpm_data)):
            # Simplificação: idealmente, RPM e acelerador deveriam estar correlacionados positivamente
            # e dentro de uma faixa ideal para cada marcha.
            # Aqui, uma métrica simples de 


            # alinhamento entre RPM e acelerador.
            # Ex: Se RPM alto e acelerador baixo, pode ser ineficiente.
            # Se RPM baixo e acelerador alto, pode ser ineficiente.
            
            # Normaliza para 0-1
            norm_rpm = rpm_data[i] / 10000.0 # Assumindo RPM máximo de 10000
            norm_throttle = throttle_data[i] / 100.0
            
            # Penaliza grandes desvios da linha y=x
            efficiency_score += (1 - abs(norm_rpm - norm_throttle))
            
        return efficiency_score / len(rpm_data) * 100.0 if len(rpm_data) > 0 else 0.0

    def _count_rev_limit_hits(self, rpm_data: np.ndarray, rev_limit_threshold: float = 9500) -> int:
        """Conta o número de vezes que o limite de rotações foi atingido."""
        if len(rpm_data) == 0:
            return 0
        
        hits = 0
        for i in range(1, len(rpm_data)):
            if rpm_data[i] >= rev_limit_threshold and rpm_data[i-1] < rev_limit_threshold:
                hits += 1
        return hits

    def _calculate_grip_utilization(self, g_lat_data: np.ndarray, speed_data: np.ndarray) -> float:
        """Estima a utilização da aderência (grip) com base nas forças G laterais e velocidade."""
        if len(g_lat_data) != len(speed_data) or len(g_lat_data) == 0:
            return 0.0
        
        # Simplificação: A utilização da aderência é maior quando as forças G laterais são altas
        # em velocidades razoáveis. Pode ser comparado com o potencial máximo de Gs para o carro/pneu.
        
        # Média das forças G laterais absolutas em movimento
        active_g_lat = [abs(g) for g, speed in zip(g_lat_data, speed_data) if speed > 10]
        
        if not active_g_lat:
            return 0.0
            
        avg_g_lat = np.mean(active_g_lat)
        
        # Assumindo um G lateral máximo teórico de 2.0 para carros de corrida
        max_theoretical_g = 2.0
        
        utilization = (avg_g_lat / max_theoretical_g) * 100.0
        return min(100.0, utilization)

    def _detect_tire_slip_events(self, g_lat_data: np.ndarray, speed_data: np.ndarray = None, threshold_g_drop: float = 0.3) -> int:
        """Detecta eventos de escorregamento de pneu (queda súbita de G lateral)."""
        if len(g_lat_data) < 2:
            return 0
        
        slip_events = 0
        for i in range(1, len(g_lat_data)):
            # Queda significativa na força G lateral
            if g_lat_data[i-1] > 0.5 and (g_lat_data[i-1] - g_lat_data[i]) > threshold_g_drop:
                slip_events += 1
            elif g_lat_data[i-1] < -0.5 and (g_lat_data[i] - g_lat_data[i-1]) > threshold_g_drop:
                slip_events += 1
        return slip_events

    def _analyze_cornering_performance(self, g_lat_data: np.ndarray, speed_data: np.ndarray) -> Dict[str, Any]:
        """Analisa a performance em curvas (velocidade vs. G lateral)."""
        if len(g_lat_data) != len(speed_data) or len(g_lat_data) == 0:
            return {"valid": False}
        
        cornering_speeds = []
        cornering_g_forces = []
        
        for g, speed in zip(g_lat_data, speed_data):
            if abs(g) > 0.5 and speed > 30: # Considera apenas curvas significativas
                cornering_speeds.append(speed)
                cornering_g_forces.append(abs(g))
                
        if not cornering_speeds:
            return {"valid": False}
            
        analysis = {
            "valid": True,
            "avg_cornering_speed": float(np.mean(cornering_speeds)),
            "max_cornering_g": float(np.max(cornering_g_forces)),
            "avg_cornering_g": float(np.mean(cornering_g_forces)),
            "g_speed_ratio": float(np.mean(np.array(cornering_g_forces) / np.array(cornering_speeds))) if np.mean(cornering_speeds) > 0 else 0.0
        }
        
        return analysis

    def _estimate_tire_degradation(self, channels_data: Dict[str, List[float]]) -> float:
        """Estima a degradação dos pneus com base em múltiplas métricas."""
        # Isso é uma estimativa complexa e requer dados de longo prazo ou específicos de pneu.
        # Simplificação: aumento de correções de direção, diminuição de G lateral máximo,
        # aumento de tempo de volta, etc.
        
        # Para esta versão, vamos usar uma heurística simples:
        # Se houver um aumento significativo na variância da direção e uma queda na média de G lateral
        # ao longo das voltas, pode indicar degradação.
        
        # Placeholder para uma análise mais robusta.
        return 0.0 # Retorna 0.0 por enquanto, pois requer dados de múltiplas voltas e um modelo mais complexo

    def _estimate_fuel_consumption_rate(self, throttle_data: np.ndarray, rpm_data: np.ndarray, sample_rate: float = 60.0) -> float:
        """Estima a taxa de consumo de combustível (litros/hora ou litros/volta)."""
        if len(throttle_data) != len(rpm_data) or len(throttle_data) == 0:
            return 0.0
        
        # Modelo simplificado: consumo é proporcional ao acelerador e RPM
        # Coeficientes são arbitrários para demonstração
        fuel_factor = 0.0001 # Litros por unidade de (acelerador * RPM) por segundo
        
        total_consumption_units = np.sum((throttle_data / 100.0) * (rpm_data / 10000.0)) # Normaliza
        
        # Converte para litros por hora (assumindo 60Hz)
        consumption_per_second = total_consumption_units * fuel_factor
        consumption_per_hour = consumption_per_second * 3600
        
        return consumption_per_hour

    def _calculate_fuel_efficiency_score(self, throttle_data: np.ndarray, rpm_data: np.ndarray, speed_data: np.ndarray) -> float:
        """Calcula um score de eficiência de combustível (velocidade vs. consumo)."""
        if len(throttle_data) != len(rpm_data) or len(throttle_data) != len(speed_data) or len(throttle_data) == 0:
            return 0.0
        
        # Quanto mais velocidade por menos consumo, melhor
        # Consumo estimado por ponto de dados
        consumption_per_point = (throttle_data / 100.0) * (rpm_data / 10000.0)
        
        # Evita divisão por zero
        consumption_per_point[consumption_per_point == 0] = 1e-6
        
        efficiency_per_point = speed_data / consumption_per_point
        
        return float(np.mean(efficiency_per_point)) if len(efficiency_per_point) > 0 else 0.0

    def _analyze_sectors(self, lap_data: Dict[str, Any], channels_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Analisa os setores da volta."""
        # Requer informações de setores no metadata ou cálculo dinâmico
        # Para esta versão, vamos simular 3 setores baseados em tempo
        
        lap_time = lap_data.get("lap_time", 0)
        data_points = lap_data.get("data_points", [])
        
        if lap_time == 0 or not data_points:
            return []
            
        sector_times = []
        sector_start_index = 0
        
        # Divide a volta em 3 setores iguais por tempo
        sector_duration = lap_time / 3.0
        
        for i in range(3):
            end_time = (i + 1) * sector_duration
            
            # Encontra o índice do ponto de dados mais próximo do tempo final do setor
            sector_end_index = sector_start_index
            for j in range(sector_start_index, len(data_points)):
                if data_points[j].get("Time", 0) >= end_time:
                    sector_end_index = j
                    break
            else:
                sector_end_index = len(data_points) - 1 # Último setor
            
            sector_data_points = data_points[sector_start_index : sector_end_index + 1]
            
            if sector_data_points:
                sector_time = sector_data_points[-1].get("Time", 0) - sector_data_points[0].get("Time", 0)
                
                # Análise simplificada do setor
                sector_speeds = [p.get("SPEED", 0) for p in sector_data_points]
                sector_throttles = [p.get("THROTTLE", 0) for p in sector_data_points]
                sector_brakes = [p.get("BRAKE", 0) for p in sector_data_points]
                
                sector_analysis = {
                    "id": i + 1,
                    "time": sector_time,
                    "avg_speed": float(np.mean(sector_speeds)) if sector_speeds else 0.0,
                    "avg_throttle": float(np.mean(sector_throttles)) if sector_throttles else 0.0,
                    "avg_brake": float(np.mean(sector_brakes)) if sector_brakes else 0.0,
                    "max_speed": float(np.max(sector_speeds)) if sector_speeds else 0.0,
                    "min_speed": float(np.min(sector_speeds)) if sector_speeds else 0.0,
                }
                sector_times.append(sector_analysis)
            
            sector_start_index = sector_end_index + 1
            
        return sector_times

    def _calculate_efficiency_metrics(self, channels_data: Dict[str, List[float]]) -> Dict[str, float]:
        """Calcula métricas de eficiência geral."""
        speed_data = np.array(channels_data.get("speed", []))
        throttle_data = np.array(channels_data.get("throttle", []))
        brake_data = np.array(channels_data.get("brake", []))
        steering_data = np.array(channels_data.get("steering", []))
        
        metrics = {
            "overall_smoothness": float(np.mean([
                self._calculate_input_smoothness(throttle_data),
                self._calculate_input_smoothness(brake_data),
                self._calculate_input_smoothness(steering_data)
            ])),
            "energy_recovery_potential": 0.0, # Placeholder
            "lap_time_consistency_score": self._calculate_speed_consistency(speed_data) # Reutiliza para consistência geral
        }
        
        return metrics

    def _calculate_performance_metrics(self, telemetry_data: Dict[str, Any]) -> List[PerformanceMetric]:
        """Calcula métricas de performance chave."""
        overview = self._analyze_session_overview(telemetry_data)
        
        metrics = []
        
        if overview:
            metrics.append(PerformanceMetric("Melhor Tempo de Volta", overview.get("best_lap_time", 0), "s", "Tempo"))
            metrics.append(PerformanceMetric("Velocidade Máxima", overview.get("top_speed", 0), "km/h", "Velocidade"))
            metrics.append(PerformanceMetric("Velocidade Média", overview.get("average_lap_time", 0), "km/h", "Velocidade"))
            metrics.append(PerformanceMetric("Consistência de Volta", overview.get("lap_time_std", 0), "s", "Consistência"))
            metrics.append(PerformanceMetric("Aceleração Total", overview.get("total_acceleration", 0), "m/s²", "Forças G"))
            metrics.append(PerformanceMetric("Frenagem Total", overview.get("total_braking", 0), "m/s²", "Forças G"))
            
        # Adicionar mais métricas baseadas em análises de volta
        
        return metrics

    def _generate_driver_insights(self, telemetry_data: Dict[str, Any]) -> List[DriverInsight]:
        """Gera insights acionáveis para o piloto."""
        insights = []
        
        overview = self._analyze_session_overview(telemetry_data)
        if overview.get("improvement_trend") == "declining":
            insights.append(DriverInsight(
                category="Consistência",
                title="Queda na Consistência de Volta",
                description="Seus tempos de volta estão piorando ao longo da sessão. Isso pode indicar fadiga, degradação dos pneus ou perda de foco.",
                severity="warning",
                recommendation="Foque em manter uma linha consistente e entradas suaves. Considere um pit stop para pneus novos se for uma corrida longa.",
                data_points=[]
            ))
            
        # Exemplo: Aceleração ineficiente
        for lap_analysis in self._analyze_all_laps(telemetry_data):
            throttle_analysis = lap_analysis.get("throttle_analysis", {})
            if throttle_analysis.get("full_throttle_percentage", 0) < 60 and throttle_analysis.get("avg_throttle_position", 0) < 80:
                insights.append(DriverInsight(
                    category="Aceleração",
                    title=f"Aceleração Subutilizada na Volta {lap_analysis['lap_number']}",
                    description="Você não está usando o acelerador totalmente em muitas partes da volta, perdendo potencial de velocidade.",
                    severity="info",
                    recommendation="Tente aplicar mais acelerador mais cedo na saída das curvas, mas com cuidado para não perder tração.",
                    data_points=[throttle_analysis.get("full_throttle_percentage", 0)]
                ))
                
        # Exemplo: Frenagem excessiva
        for lap_analysis in self._analyze_all_laps(telemetry_data):
            brake_analysis = lap_analysis.get("brake_analysis", {})
            if brake_analysis.get("max_brake_pressure", 0) > 90 and brake_analysis.get("braking_events", 0) > 5:
                insights.append(DriverInsight(
                    category="Frenagem",
                    title=f"Frenagem Excessiva na Volta {lap_analysis['lap_number']}",
                    description="Você está aplicando muita pressão de freio ou freando em excesso, o que pode levar a travamentos e perda de tempo.",
                    severity="warning",
                    recommendation="Tente modular o freio, usando menos pressão no início e liberando gradualmente (trail braking) para manter a velocidade de entrada na curva.",
                    data_points=[brake_analysis.get("max_brake_pressure", 0)]
                ))
                
        # Exemplo: Subesterço
        for lap_analysis in self._analyze_all_laps(telemetry_data):
            steering_analysis = lap_analysis.get("steering_analysis", {})
            if steering_analysis.get("understeer_indication", 0) > 0.5: # Mais de 0.5s de subesterço
                insights.append(DriverInsight(
                    category="Comportamento do Carro",
                    title=f"Subesterço Detectado na Volta {lap_analysis['lap_number']}",
                    description="O carro está apresentando subesterço significativo, o que impede você de virar o carro adequadamente.",
                    severity="warning",
                    recommendation="Verifique a pressão dos pneus dianteiros, a asa dianteira ou tente uma entrada de curva mais suave.",
                    data_points=[steering_analysis.get("understeer_indication", 0)]
                ))
                
        # Exemplo: Oversteer
        for lap_analysis in self._analyze_all_laps(telemetry_data):
            steering_analysis = lap_analysis.get("steering_analysis", {})
            if steering_analysis.get("oversteer_indication", 0) > 0.5: # Mais de 0.5s de sobreesterço
                insights.append(DriverInsight(
                    category="Comportamento do Carro",
                    title=f"Sobreesterço Detectado na Volta {lap_analysis['lap_number']}",
                    description="O carro está apresentando sobreesterço significativo, o que pode levar a rodadas.",
                    severity="warning",
                    recommendation="Verifique a pressão dos pneus traseiros, a asa traseira ou tente uma saída de curva mais suave com o acelerador.",
                    data_points=[steering_analysis.get("oversteer_indication", 0)]
                ))
                
        return insights

    def _comparative_analysis(self, telemetry_data: Dict[str, Any]) -> List[LapComparison]:
        """Realiza análise comparativa entre voltas."""
        laps = telemetry_data.get("laps", [])
        if len(laps) < 2:
            return []
        
        comparisons = []
        
        # Comparar a melhor volta com a segunda melhor, ou com a volta anterior
        # Simplificação: compara a melhor volta com a volta imediatamente anterior a ela
        
        best_lap_idx = -1
        best_lap_time = float("inf")
        for i, lap in enumerate(laps):
            if lap.get("lap_time", 0) > 0 and lap.get("lap_time", 0) < best_lap_time:
                best_lap_time = lap.get("lap_time", 0)
                best_lap_idx = i
                
        if best_lap_idx > 0:
            ref_lap = laps[best_lap_idx]
            comp_lap = laps[best_lap_idx - 1]
            
            time_delta = ref_lap.get("lap_time", 0) - comp_lap.get("lap_time", 0)
            
            # Análise de delta por setor (simplificado)
            sector_deltas = [time_delta / 3, time_delta / 3, time_delta / 3] # Placeholder
            
            # Análise de delta de velocidade (simplificado)
            ref_speeds = [p.get("SPEED", 0) for p in ref_lap.get("data_points", [])]
            comp_speeds = [p.get("SPEED", 0) for p in comp_lap.get("data_points", [])]
            
            speed_delta_avg = 0.0
            if ref_speeds and comp_speeds:
                min_len = min(len(ref_speeds), len(comp_speeds))
                speed_delta_avg = float(np.mean(np.array(ref_speeds[:min_len]) - np.array(comp_speeds[:min_len])))
            
            improvements = []
            regressions = []
            
            if time_delta < 0:
                improvements.append(f"Melhora de {abs(time_delta):.3f}s no tempo de volta.")
            else:
                regressions.append(f"Piora de {abs(time_delta):.3f}s no tempo de volta.")
                
            if speed_delta_avg > 0:
                improvements.append(f"Média de velocidade {speed_delta_avg:.1f} km/h maior.")
            elif speed_delta_avg < 0:
                regressions.append(f"Média de velocidade {abs(speed_delta_avg):.1f} km/h menor.")
            
            comparisons.append(LapComparison(
                reference_lap=ref_lap.get("lap_number", 0),
                comparison_lap=comp_lap.get("lap_number", 0),
                time_delta=time_delta,
                sector_deltas=sector_deltas,
                speed_delta_avg=speed_delta_avg,
                improvements=improvements,
                regressions=regressions
            ))
            
        return comparisons

    def _predictive_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análises preditivas (ex: tempo de volta ideal, consumo de combustível)."""
        laps = telemetry_data.get("laps", [])
        if not laps:
            return {}
            
        # Tempo de volta ideal (best theoretical lap)
        # Soma dos melhores setores de todas as voltas
        best_sector_times = [float("inf")] * 3 # Assumindo 3 setores
        
        for lap in laps:
            sector_analysis = self._analyze_sectors(lap, self._extract_channels_data(lap.get("data_points", [])))
            for sector in sector_analysis:
                sector_id = sector.get("id", 0) - 1
                if 0 <= sector_id < 3:
                    best_sector_times[sector_id] = min(best_sector_times[sector_id], sector.get("time", float("inf")))
                    
        best_theoretical_lap = sum(s for s in best_sector_times if s != float("inf"))
        
        # Previsão de consumo de combustível para a corrida
        overview = self._analyze_session_overview(telemetry_data)
        estimated_consumption_rate = overview.get("estimated_consumption_rate", 0.0) # Litros/hora
        
        # Assumindo uma corrida de 1 hora para exemplo
        predicted_fuel_needed_1hr = estimated_consumption_rate
        
        return {
            "best_theoretical_lap_time": best_theoretical_lap,
            "predicted_fuel_needed_1hr": predicted_fuel_needed_1hr
        }

    def _generate_setup_recommendations(self, telemetry_data: Dict[str, Any]) -> List[str]:
        """Gera recomendações de setup com base na análise."""
        recommendations = []
        
        # Exemplo: Se muito subesterço, sugerir ajuste na asa dianteira
        for insight in self._generate_driver_insights(telemetry_data):
            if insight.category == "Comportamento do Carro" and "Subesterço" in insight.title:
                recommendations.append("Aumentar asa dianteira ou diminuir asa traseira para reduzir subesterço.")
            elif insight.category == "Comportamento do Carro" and "Sobreesterço" in insight.title:
                recommendations.append("Diminuir asa dianteira ou aumentar asa traseira para reduzir sobreesterço.")
        
        # Exemplo: Se frenagem ineficiente, sugerir ajuste de balanço de freio
        for lap_analysis in self._analyze_all_laps(telemetry_data):
            brake_analysis = lap_analysis.get("brake_analysis", {})
            if brake_analysis.get("braking_efficiency", 0) < 0.5: # Limiar arbitrário
                recommendations.append("Ajustar balanço de freio para otimizar a frenagem.")
                
        return list(set(recommendations)) # Remove duplicatas

    def _analyze_consistency(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a consistência do piloto em diferentes aspectos."""
        laps = telemetry_data.get("laps", [])
        if not laps:
            return {}
            
        lap_times = [lap.get("lap_time", 0) for lap in laps if lap.get("lap_time", 0) > 0]
        
        consistency = {
            "lap_time_std": float(np.std(lap_times)) if lap_times else 0.0,
            "lap_time_range": float(np.max(lap_times) - np.min(lap_times)) if lap_times else 0.0,
            "speed_consistency_avg": float(np.mean([self._analyze_single_lap(lap, i+1, telemetry_data).get("speed_analysis", {}).get("speed_consistency", 0) for i, lap in enumerate(laps) if lap.get("data_points")])) if laps else 0.0,
            "throttle_smoothness_avg": float(np.mean([self._analyze_single_lap(lap, i+1, telemetry_data).get("throttle_analysis", {}).get("throttle_smoothness", 0) for i, lap in enumerate(laps) if lap.get("data_points")])) if laps else 0.0,
            "brake_smoothness_avg": float(np.mean([self._analyze_single_lap(lap, i+1, telemetry_data).get("brake_analysis", {}).get("brake_smoothness", 0) for i, lap in enumerate(laps) if lap.get("data_points")])) if laps else 0.0,
            "steering_smoothness_avg": float(np.mean([self._analyze_single_lap(lap, i+1, telemetry_data).get("steering_analysis", {}).get("steering_smoothness", 0) for i, lap in enumerate(laps) if lap.get("data_points")])) if laps else 0.0,
        }
        
        return consistency

    def _analyze_weather_conditions(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa as condições climáticas (se disponíveis nos dados)."""
        # Requer canais como 'AirTemp', 'TrackTemp', 'Rain', etc.
        # Para esta versão, apenas um placeholder.
        metadata = telemetry_data.get("metadata", {})
        return {
            "air_temp": metadata.get("air_temperature", "N/A"),
            "track_temp": metadata.get("track_temperature", "N/A"),
            "rain": metadata.get("rain_level", "N/A"),
            "wet_track": metadata.get("wet_track", "N/A")
        }

    def _detect_session_type(self, telemetry_data: Dict[str, Any]) -> str:
        """Detecta o tipo de sessão (prática, qualificação, corrida)."""
        metadata = telemetry_data.get("metadata", {})
        session_type = metadata.get("session_type", "Unknown").lower()
        
        if "practice" in session_type:
            return "Practice"
        elif "qualifying" in session_type or "quali" in session_type:
            return "Qualifying"
        elif "race" in session_type:
            return "Race"
        else:
            return "Other"

    def _calculate_improvement_trend(self, lap_times: List[float]) -> str:
        """Calcula a tendência de melhoria dos tempos de volta."""
        if len(lap_times) < 3:
            return "stable"
        
        # Regressão linear simples para ver a tendência
        x = np.arange(len(lap_times))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, lap_times)
        
        if slope < -0.01: # Tempos diminuindo
            return "improving"
        elif slope > 0.01: # Tempos aumentando
            return "declining"
        else:
            return "stable"

    def _format_time(self, time_seconds: float) -> str:
        """Formata tempo em segundos para MM:SS.mmm."""
        if time_seconds <= 0:
            return "00:00.000"
        
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 1000)
        
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


