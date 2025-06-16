"""
Módulo de comparação de telemetria para o Race Telemetry Analyzer.
Responsável por comparar dados de telemetria entre diferentes voltas e identificar pontos de melhoria.
Permite a comparação de múltiplas voltas.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from scipy.interpolate import interp1d
from scipy.spatial.distance import cdist
import itertools

class TelemetryComparison:
    """Classe principal para comparação de dados de telemetria entre múltiplas voltas."""

    def __init__(self):
        """Inicializa o comparador de telemetria."""
        # Métodos de comparação ainda podem ser úteis internamente ou para comparações específicas
        self.comparison_methods = {
            'distance': self._compare_laps_by_distance,
            'time': self._compare_laps_by_time,
            'position': self._compare_laps_by_position
        }

    def compare_multiple_laps(self, laps: List[Dict[str, Any]], reference_lap_index: int = 0, method: str = 'distance') -> List[Dict[str, Any]]:
        """
        Compara múltiplas voltas contra uma volta de referência.

        Args:
            laps: Lista de dicionários, cada um contendo dados de uma volta.
            reference_lap_index: Índice da volta na lista 'laps' a ser usada como referência.
            method: Método de comparação ('distance', 'time', 'position').

        Returns:
            Lista de dicionários, cada um contendo o resultado da comparação
            de uma volta contra a volta de referência.
        """
        if not laps or len(laps) < 2:
            raise ValueError("Pelo menos duas voltas são necessárias para comparação.")

        if reference_lap_index < 0 or reference_lap_index >= len(laps):
            raise ValueError("Índice da volta de referência inválido.")

        if method not in self.comparison_methods:
            raise ValueError(f"Método de comparação não suportado: {method}")

        reference_lap = laps[reference_lap_index]
        comparison_results = []

        compare_func = self.comparison_methods[method]

        for i, comparison_lap in enumerate(laps):
            if i == reference_lap_index:
                continue # Não compara a volta de referência com ela mesma

            try:
                result = compare_func(reference_lap, comparison_lap)
                comparison_results.append(result)
            except Exception as e:
                print(f"Erro ao comparar volta {comparison_lap.get('lap_number', i)} com a volta de referência {reference_lap.get('lap_number', reference_lap_index)}: {e}")
                # Adiciona um resultado de erro ou pula esta comparação
                comparison_results.append({
                    'reference_lap': reference_lap.get('lap_number', reference_lap_index),
                    'comparison_lap': comparison_lap.get('lap_number', i),
                    'error': str(e)
                })

        return comparison_results

    # Renomeando métodos internos para clareza (eram _compare_by_distance, etc.)
    def _compare_laps_by_distance(self, reference_lap: Dict[str, Any], comparison_lap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara duas voltas usando a distância percorrida como referência.
        (Lógica interna adaptada da versão anterior)
        """
        ref_points = reference_lap.get('data_points', [])
        comp_points = comparison_lap.get('data_points', [])

        if len(ref_points) < 10 or len(comp_points) < 10:
             # Retorna um erro estruturado em vez de lançar exceção direta aqui
             # para permitir que o loop em compare_multiple_laps continue
            return {
                'reference_lap': reference_lap.get('lap_number', 'N/A'),
                'comparison_lap': comparison_lap.get('lap_number', 'N/A'),
                'error': "Dados insuficientes para comparação (menos de 10 pontos)"
            }

        try:
            # Extrai distâncias e tempos, tratando possíveis erros de chave
            ref_distances = [p['distance'] for p in ref_points if 'distance' in p]
            ref_times = [p['time'] for p in ref_points if 'time' in p]
            comp_distances = [p['distance'] for p in comp_points if 'distance' in p]
            comp_times = [p['time'] for p in comp_points if 'time' in p]

            if not ref_distances or not ref_times or not comp_distances or not comp_times:
                 raise ValueError("Dados de distância ou tempo ausentes nos pontos de dados.")

            # Garante que os dados tenham o mesmo comprimento após extração
            min_len_ref = min(len(ref_distances), len(ref_times))
            min_len_comp = min(len(comp_distances), len(comp_times))
            ref_distances, ref_times = ref_distances[:min_len_ref], ref_times[:min_len_ref]
            comp_distances, comp_times = comp_distances[:min_len_comp], comp_times[:min_len_comp]

            # Verifica novamente se há pontos suficientes após a limpeza
            if len(ref_distances) < 10 or len(comp_distances) < 10:
                raise ValueError("Dados insuficientes após validação de distância/tempo.")

            # Normaliza as distâncias para 0-1 (ou usa distância absoluta se preferir)
            max_ref_dist = max(ref_distances) if ref_distances else 1.0
            max_comp_dist = max(comp_distances) if comp_distances else 1.0
            # Evita divisão por zero se a distância for zero
            norm_ref_dist = np.array([d / max_ref_dist if max_ref_dist > 0 else 0 for d in ref_distances])
            norm_comp_dist = np.array([d / max_comp_dist if max_comp_dist > 0 else 0 for d in comp_distances])

            # Remove duplicatas nas distâncias normalizadas antes da interpolação
            norm_ref_dist, unique_ref_indices = np.unique(norm_ref_dist, return_index=True)
            ref_times_unique = np.array(ref_times)[unique_ref_indices]

            norm_comp_dist, unique_comp_indices = np.unique(norm_comp_dist, return_index=True)
            comp_times_unique = np.array(comp_times)[unique_comp_indices]

            # Verifica se ainda há pontos suficientes após unique
            if len(norm_ref_dist) < 2 or len(norm_comp_dist) < 2:
                 raise ValueError("Pontos insuficientes para interpolação após remover duplicatas.")

            # Cria interpoladores para os tempos
            ref_time_interp = interp1d(norm_ref_dist, ref_times_unique, kind='linear', bounds_error=False, fill_value='extrapolate')
            comp_time_interp = interp1d(norm_comp_dist, comp_times_unique, kind='linear', bounds_error=False, fill_value='extrapolate')

            # Cria pontos de amostragem uniformes (baseados na distância normalizada 0-1)
            num_samples = max(len(ref_points), len(comp_points)) # Ajusta o número de amostras
            sample_points_norm_dist = np.linspace(0, 1, num_samples)

            # Interpola os tempos nos pontos de amostragem
            ref_times_sampled = ref_time_interp(sample_points_norm_dist)
            comp_times_sampled = comp_time_interp(sample_points_norm_dist)

            # Calcula o delta de tempo (positivo significa que a volta de comparação é mais lenta)
            # Ajusta os tempos para começar em 0 relativo ao início da amostragem
            ref_times_sampled_relative = ref_times_sampled - ref_times_sampled[0]
            comp_times_sampled_relative = comp_times_sampled - comp_times_sampled[0]
            delta_times = comp_times_sampled_relative - ref_times_sampled_relative

            # Calcula o delta cumulativo (este cálculo parece incorreto, deve ser a integral do delta instantâneo)
            # O delta cumulativo em um ponto de distância d é simplesmente delta_times nesse ponto d.
            # O que pode ser útil é o delta *instantâneo* (derivada do delta_time em relação à distância)
            # Mas por ora, manteremos o delta_times como está (diferença de tempo no mesmo ponto de distância normalizada)

            # Interpola outros canais para análise (ex: velocidade)
            # Precisa de tratamento semelhante para unique e interpolação
            ref_speeds = [p['speed'] for p in ref_points if 'speed' in p]
            comp_speeds = [p['speed'] for p in comp_points if 'speed' in p]
            ref_speeds_unique = np.array(ref_speeds)[unique_ref_indices]
            comp_speeds_unique = np.array(comp_speeds)[unique_comp_indices]

            ref_speed_interp = interp1d(norm_ref_dist, ref_speeds_unique, kind='linear', bounds_error=False, fill_value='extrapolate')
            comp_speed_interp = interp1d(norm_comp_dist, comp_speeds_unique, kind='linear', bounds_error=False, fill_value='extrapolate')

            ref_speeds_sampled = ref_speed_interp(sample_points_norm_dist)
            comp_speeds_sampled = comp_speed_interp(sample_points_norm_dist)

            # Identifica pontos de ganho e perda (simplificado)
            # Um ponto de perda significa que delta_times > 0 (comp mais lento)
            # Um ponto de ganho significa que delta_times < 0 (comp mais rápido)
            gain_points = []
            loss_points = []
            threshold = 0.01 # 10ms

            for i in range(num_samples):
                delta = delta_times[i]
                dist_val = sample_points_norm_dist[i] * max_ref_dist # Distância real aproximada
                # Encontrar ponto original mais próximo para obter posição (pode ser impreciso)
                # closest_ref_idx = self._find_closest_point_by_distance(ref_points, dist_val)
                # position = ref_points[closest_ref_idx]['position'] if closest_ref_idx is not None else [0,0]

                point_info = {
                    'distance_norm': sample_points_norm_dist[i],
                    'distance_abs': dist_val,
                    'delta': delta,
                    'speed_ref': ref_speeds_sampled[i],
                    'speed_comp': comp_speeds_sampled[i],
                    # 'position': position # Adicionar se a busca por ponto próximo for implementada
                }
                if delta < -threshold:
                    gain_points.append({**point_info, 'type': 'gain'})
                elif delta > threshold:
                    loss_points.append({**point_info, 'type': 'loss'})

            # Analisa os setores (se disponíveis)
            sector_analysis = self._analyze_sectors(reference_lap, comparison_lap)

            # Identifica pontos-chave (frenagem, ápice, aceleração) - Placeholder
            key_points_analysis = self._identify_key_points(reference_lap, comparison_lap)

            # Prepara o resultado da comparação
            comparison_result = {
                'reference_lap': reference_lap.get('lap_number', 'N/A'),
                'comparison_lap': comparison_lap.get('lap_number', 'N/A'),
                'reference_lap_time': reference_lap.get('lap_time', 0),
                'comparison_lap_time': comparison_lap.get('lap_time', 0),
                'time_delta_total': comparison_lap.get('lap_time', 0) - reference_lap.get('lap_time', 0),
                'sectors': sector_analysis,
                'delta_samples': {
                    'distance_norm': sample_points_norm_dist.tolist(),
                    'distance_abs': (sample_points_norm_dist * max_ref_dist).tolist(),
                    'delta_time': delta_times.tolist(),
                    'ref_time_sampled': ref_times_sampled_relative.tolist(),
                    'comp_time_sampled': comp_times_sampled_relative.tolist(),
                    'ref_speed_sampled': ref_speeds_sampled.tolist(),
                    'comp_speed_sampled': comp_speeds_sampled.tolist(),
                },
                'key_differences': {
                    'gain_points': gain_points, # Pontos onde comp foi mais rápido
                    'loss_points': loss_points, # Pontos onde comp foi mais lento
                    'key_points': key_points_analysis
                },
                'improvement_suggestions': [] # Placeholder para sugestões futuras
                # 'improvement_suggestions': self._generate_improvement_suggestions(gain_points, loss_points, key_points_analysis)
            }

            return comparison_result

        except Exception as e:
            # Captura erros durante o processamento da comparação
            return {
                'reference_lap': reference_lap.get('lap_number', 'N/A'),
                'comparison_lap': comparison_lap.get('lap_number', 'N/A'),
                'error': f"Erro interno na comparação por distância: {str(e)}"
            }

    def _compare_laps_by_time(self, reference_lap: Dict[str, Any], comparison_lap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara duas voltas usando o tempo como referência.
        (Implementação precisa ser adaptada/verificada para robustez)
        """
        # Placeholder - A lógica precisa ser revisada e adaptada similarmente a _compare_laps_by_distance
        print("Aviso: Comparação por tempo ainda não totalmente implementada/validada.")
        # Simplificado para retornar estrutura básica
        return {
            'reference_lap': reference_lap.get('lap_number', 'N/A'),
            'comparison_lap': comparison_lap.get('lap_number', 'N/A'),
            'reference_lap_time': reference_lap.get('lap_time', 0),
            'comparison_lap_time': comparison_lap.get('lap_time', 0),
            'time_delta_total': comparison_lap.get('lap_time', 0) - reference_lap.get('lap_time', 0),
            'sectors': self._analyze_sectors(reference_lap, comparison_lap),
            'error': 'Comparação por tempo não implementada completamente.'
        }

    def _compare_laps_by_position(self, reference_lap: Dict[str, Any], comparison_lap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara duas voltas usando a posição na pista como referência.
        (Implementação precisa ser adaptada/verificada para robustez)
        """
         # Placeholder - A lógica precisa ser revisada e adaptada similarmente a _compare_laps_by_distance
        print("Aviso: Comparação por posição ainda não totalmente implementada/validada.")
        # Simplificado para retornar estrutura básica
        return {
            'reference_lap': reference_lap.get('lap_number', 'N/A'),
            'comparison_lap': comparison_lap.get('lap_number', 'N/A'),
            'reference_lap_time': reference_lap.get('lap_time', 0),
            'comparison_lap_time': comparison_lap.get('lap_time', 0),
            'time_delta_total': comparison_lap.get('lap_time', 0) - reference_lap.get('lap_time', 0),
            'sectors': self._analyze_sectors(reference_lap, comparison_lap),
            'error': 'Comparação por posição não implementada completamente.'
        }

    def _analyze_sectors(self, reference_lap: Dict[str, Any], comparison_lap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa e compara os tempos de setor entre duas voltas."""
        ref_sectors = reference_lap.get('sectors', [])
        comp_sectors = comparison_lap.get('sectors', [])
        sector_analysis = []

        # Assume que os setores estão ordenados e correspondem
        num_sectors = min(len(ref_sectors), len(comp_sectors))

        for i in range(num_sectors):
            ref_sector_time = ref_sectors[i].get('time', 0)
            comp_sector_time = comp_sectors[i].get('time', 0)
            delta = comp_sector_time - ref_sector_time
            sector_analysis.append({
                'sector': i + 1,
                'ref_time': ref_sector_time,
                'comp_time': comp_sector_time,
                'delta': delta
            })

        # Adiciona setores restantes se houver diferença no número
        if len(ref_sectors) > num_sectors:
            for i in range(num_sectors, len(ref_sectors)):
                 sector_analysis.append({'sector': i + 1, 'ref_time': ref_sectors[i].get('time', 0), 'comp_time': None, 'delta': None})
        elif len(comp_sectors) > num_sectors:
             for i in range(num_sectors, len(comp_sectors)):
                 sector_analysis.append({'sector': i + 1, 'ref_time': None, 'comp_time': comp_sectors[i].get('time', 0), 'delta': None})

        return sector_analysis

    def _identify_key_points(self, reference_lap: Dict[str, Any], comparison_lap: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica e compara pontos chave (frenagem, ápice, aceleração). Placeholder."""
        # Esta função requer algoritmos mais sofisticados para detectar curvas,
        # pontos de frenagem (pico de desaceleração ou início de aplicação do freio),
        # ápices (menor velocidade ou maior aceleração lateral na curva) e
        # pontos de reaceleração (fim da frenagem/início da aceleração).
        # Por enquanto, retorna uma estrutura vazia.
        return {
            'braking_zones': [],
            'apexes': [],
            'acceleration_zones': []
        }

    def _find_closest_point_by_distance(self, points: List[Dict[str, Any]], target_distance: float) -> Optional[int]:
        """Encontra o índice do ponto mais próximo de uma distância alvo."""
        if not points:
            return None
        distances = np.array([p.get('distance', -1) for p in points])
        valid_indices = np.where(distances >= 0)[0]
        if len(valid_indices) == 0:
            return None
        # Calcula a diferença absoluta e encontra o índice do mínimo
        diffs = np.abs(distances[valid_indices] - target_distance)
        closest_original_index = valid_indices[np.argmin(diffs)]
        return closest_original_index

    def _interpolate_value_at_distance(self, points: List[Dict[str, Any]], channel: str, target_distance: float) -> Optional[float]:
        """Interpola o valor de um canal em uma distância específica."""
        try:
            distances = [p['distance'] for p in points if 'distance' in p and channel in p]
            values = [p[channel] for p in points if 'distance' in p and channel in p]

            if len(distances) < 2:
                return None

            # Garante que distâncias e valores tenham o mesmo comprimento
            min_len = min(len(distances), len(values))
            distances = np.array(distances[:min_len])
            values = np.array(values[:min_len])

            # Remove duplicatas nas distâncias
            distances, unique_indices = np.unique(distances, return_index=True)
            values_unique = values[unique_indices]

            if len(distances) < 2:
                return None

            interp_func = interp1d(distances, values_unique, kind='linear', bounds_error=False, fill_value=None) # Retorna None fora dos limites
            interpolated_value = interp_func(target_distance)

            # interp1d retorna array, pegamos o valor escalar
            return float(interpolated_value) if interpolated_value is not None else None
        except Exception:
            return None # Retorna None em caso de erro na interpolação

    def _generate_improvement_suggestions(self, gain_points: List[Dict], loss_points: List[Dict], key_points: Dict) -> List[str]:
        """Gera sugestões de melhoria com base nas diferenças encontradas. Placeholder."""
        suggestions = []
        # Lógica futura para analisar os pontos de ganho/perda e pontos chave
        # Exemplo: "Na curva X (distância Y), você freou mais tarde mas perdeu tempo na saída (velocidade menor). Tente otimizar a reaceleração."
        # Exemplo: "Você ganhou tempo no setor Z consistentemente. Analise a telemetria desse trecho para replicar."

        # Contagem simples por enquanto
        if loss_points:
            suggestions.append(f"Identificados {len(loss_points)} pontos principais onde a volta comparada foi mais lenta.")
        if gain_points:
             suggestions.append(f"Identificados {len(gain_points)} pontos principais onde a volta comparada foi mais rápida.")

        if not suggestions:
            suggestions.append("As voltas foram muito similares ou não foi possível gerar sugestões automáticas.")

        return suggestions

# Exemplo de uso (pode ser movido para testes)
if __name__ == '__main__':
    # Criar dados de voltas dummy para teste
    lap1_data = {
        'lap_number': 1,
        'lap_time': 90.5,
        'sectors': [{'sector': 1, 'time': 30.1}, {'sector': 2, 'time': 30.2}, {'sector': 3, 'time': 30.2}],
        'data_points': [
            {'time': t * 0.1, 'distance': t * 5.0, 'speed': 100 + t, 'position': [t * 10, t * 5], 'brake': 0.0, 'throttle': 1.0} for t in range(905)
        ]
    }
    lap2_data = {
        'lap_number': 2,
        'lap_time': 91.0, # 0.5s mais lenta
        'sectors': [{'sector': 1, 'time': 30.3}, {'sector': 2, 'time': 30.3}, {'sector': 3, 'time': 30.4}],
        'data_points': [
            # Simula ser mais lento em alguns pontos
            {'time': t * 0.1005, 'distance': t * 4.95, 'speed': 98 + t, 'position': [t * 9.9, t * 5.1], 'brake': 0.0, 'throttle': 0.98} for t in range(905)
        ]
    }
    lap3_data = {
        'lap_number': 3,
        'lap_time': 90.0, # 0.5s mais rápida
        'sectors': [{'sector': 1, 'time': 30.0}, {'sector': 2, 'time': 30.0}, {'sector': 3, 'time': 30.0}],
        'data_points': [
             {'time': t * 0.0995, 'distance': t * 5.05, 'speed': 102 + t, 'position': [t * 10.1, t * 4.9], 'brake': 0.0, 'throttle': 1.0} for t in range(905)
        ]
    }

    laps_to_compare = [lap1_data, lap2_data, lap3_data]

    comparer = TelemetryComparison()

    try:
        print("Comparando por Distância (Lap 1 como referência):")
        results_dist = comparer.compare_multiple_laps(laps_to_compare, reference_lap_index=0, method='distance')
        for result in results_dist:
            if 'error' in result:
                print(f"  Erro comparando Lap {result['reference_lap']} vs Lap {result['comparison_lap']}: {result['error']}")
            else:
                print(f"  Lap {result['reference_lap']} vs Lap {result['comparison_lap']}: Delta Total = {result['time_delta_total']:.3f}s")
                # print(f"    Sugestões: {result.get('improvement_suggestions')}")
                print(f"    Setores: {result.get('sectors')}")
                print(f"    Pontos de Perda (Comp mais lento): {len(result.get('key_differences', {}).get('loss_points', []))}")
                print(f"    Pontos de Ganho (Comp mais rápido): {len(result.get('key_differences', {}).get('gain_points', []))}")

    except ValueError as e:
        print(f"Erro na comparação: {e}")
    except Exception as e:
         print(f"Erro inesperado: {e}")

    # Testar com índice inválido
    # try:
    #     comparer.compare_multiple_laps(laps_to_compare, reference_lap_index=5)
    # except ValueError as e:
    #     print(f"\nTeste de índice inválido OK: {e}")

    # Testar com poucas voltas
    # try:
    #     comparer.compare_multiple_laps([lap1_data])
    # except ValueError as e:
    #     print(f"\nTeste de poucas voltas OK: {e}")

