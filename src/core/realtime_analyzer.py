"""
Real-time telemetry analysis module for Race Telemetry Analyzer.
Provides threaded analysis of telemetry data with feedback generation.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger(__name__)

class RealTimeAnalyzerWorker(QObject):
    """Worker object to perform analysis in a separate thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    feedback_detected = pyqtSignal(str)  # Signal for feedback messages
    progress_update = pyqtSignal(int, int)  # Current step, total steps
    analysis_results_ready = pyqtSignal(dict)  # Novo sinal para resultados da análise abrangente

    def __init__(self, telemetry_data: Dict[str, Any]):
        super().__init__()
        self.telemetry_data = telemetry_data
        self._running = False
        self._paused = False

    def run(self):
        """Main analysis loop."""
        try:
            self._running = True
            logger.info("🚀 RealTimeAnalyzerWorker iniciado!")
            
            # Log detalhado dos dados recebidos
            logger.info("=== DADOS RECEBIDOS NO WORKER ===")
            logger.info(f"Tipo de telemetry_data: {type(self.telemetry_data)}")
            logger.info(f"Chaves: {list(self.telemetry_data.keys())}")
            
            # Get laps from telemetry data
            laps = self.telemetry_data.get("laps", [])
            logger.info(f"🏁 Voltas para análise: {len(laps)}")
            
            if not laps:
                logger.error("❌ Nenhuma volta encontrada nos dados!")
                self.error.emit("Nenhuma volta encontrada nos dados.")
                return
                
            total_laps = len(laps)
            logger.info(f"📊 Analisando {total_laps} voltas...")
            
            # Log detalhes de cada volta
            for i, lap in enumerate(laps):
                logger.info(f"🏁 Volta {i+1}:")
                logger.info(f"   Número da volta: {lap.get('lap_number', 'N/A')}")
                logger.info(f"   Tempo da volta: {lap.get('lap_time', 'N/A')}")
                data_points = lap.get("data_points", [])
                if isinstance(data_points, list):
                    logger.info(f"   Pontos de dados: {len(data_points)}")
                else:
                    logger.info(f"   Pontos de dados: {data_points}")
                if data_points and isinstance(data_points, list) and len(data_points) > 0:
                    logger.info(f"   Primeiro ponto: {data_points[0]}")
                    logger.info(f"   Último ponto: {data_points[-1]}")
            
            # Analysis results storage
            analysis_results = {
                "laps_analyzed": 0,
                "total_laps": total_laps,
                "best_lap": None,
                "worst_lap": None,
                "average_lap_time": 0.0,
                "consistency_score": 0.0,
                "feedback_messages": [],
                "lap_details": []
            }
            
            lap_times = []
            
            for i, lap in enumerate(laps):
                if not self._running:
                    logger.info("⏹️ Análise interrompida pelo usuário")
                    break
                    
                while self._paused:
                    time.sleep(0.1)
                    if not self._running:
                        break
                
                lap_number = lap.get("lap_number", i + 1)
                lap_time = lap.get("lap_time", 0)
                
                logger.info(f"🔍 Analisando volta {lap_number} (tempo: {lap_time:.2f}s)")
                self.progress_update.emit(i + 1, total_laps)
                
                # Log detalhes da análise da volta
                data_points = lap.get("data_points", [])
                logger.info(f"   📊 Pontos de dados: {len(data_points)}")
                
                # Basic lap analysis
                lap_analysis = self._analyze_lap(lap)
                logger.info(f"   📈 Resultados da análise:")
                logger.info(f"      Velocidade média: {lap_analysis.get('average_speed', 0):.2f}")
                logger.info(f"      Velocidade máxima: {lap_analysis.get('max_speed', 0):.2f}")
                logger.info(f"      Uso de throttle: {lap_analysis.get('throttle_usage', 0):.2f}%")
                logger.info(f"      Uso de freio: {lap_analysis.get('brake_usage', 0):.2f}%")
                
                analysis_results["lap_details"].append(lap_analysis)
                
                if lap_time > 0:
                    lap_times.append(lap_time)
                    logger.info(f"   ⏱️ Tempo da volta adicionado: {lap_time:.2f}s")
                    
                    # Track best and worst laps
                    if analysis_results["best_lap"] is None or lap_time < analysis_results["best_lap"]["time"]:
                        analysis_results["best_lap"] = {"lap": lap_number, "time": lap_time}
                        logger.info(f"   🏆 Nova melhor volta: {lap_time:.2f}s")
                    if analysis_results["worst_lap"] is None or lap_time > analysis_results["worst_lap"]["time"]:
                        analysis_results["worst_lap"] = {"lap": lap_number, "time": lap_time}
                        logger.info(f"   🐌 Nova pior volta: {lap_time:.2f}s")
                else:
                    logger.warning(f"   ⚠️ Tempo da volta é 0 ou inválido")
                
                # Generate feedback for this lap
                feedback = self._generate_lap_feedback(lap_analysis)
                if feedback:
                    logger.info(f"   💬 Feedback gerado: {feedback}")
                    self.feedback_detected.emit(feedback)
                    analysis_results["feedback_messages"].append(feedback)
                
                analysis_results["laps_analyzed"] += 1
                logger.info(f"   ✅ Volta {lap_number} analisada com sucesso")
                
                # Small delay to prevent UI freezing
                time.sleep(0.01)
            
            # Calculate overall statistics
            logger.info("=== CÁLCULO DE ESTATÍSTICAS FINAIS ===")
            if lap_times:
                analysis_results["average_lap_time"] = sum(lap_times) / len(lap_times)
                logger.info(f"📊 Tempo médio das voltas: {analysis_results['average_lap_time']:.2f}s")
                
                # Calculate consistency (lower standard deviation = more consistent)
                if len(lap_times) > 1:
                    import numpy as np
                    std_dev = np.std(lap_times)
                    mean_time = np.mean(lap_times)
                    analysis_results["consistency_score"] = max(0, 100 - (std_dev / mean_time * 100))
                    logger.info(f"📊 Desvio padrão: {std_dev:.2f}s")
                    logger.info(f"📊 Consistência: {analysis_results['consistency_score']:.1f}%")
            else:
                logger.warning("⚠️ Nenhum tempo de volta válido encontrado")
            
            # Final feedback
            final_feedback = self._generate_final_feedback(analysis_results)
            if final_feedback:
                logger.info(f"💬 Feedback final: {final_feedback}")
                self.feedback_detected.emit(final_feedback)
            
            # Log resultados finais
            logger.info("=== RESULTADOS FINAIS ===")
            logger.info(f"📊 Voltas analisadas: {analysis_results['laps_analyzed']}")
            logger.info(f"📊 Total de voltas: {analysis_results['total_laps']}")
            if analysis_results['best_lap']:
                logger.info(f"🏆 Melhor volta: {analysis_results['best_lap']['lap']} em {analysis_results['best_lap']['time']:.2f}s")
            if analysis_results['worst_lap']:
                logger.info(f"🐌 Pior volta: {analysis_results['worst_lap']['lap']} em {analysis_results['worst_lap']['time']:.2f}s")
            logger.info(f"📊 Tempo médio: {analysis_results['average_lap_time']:.2f}s")
            logger.info(f"📊 Consistência: {analysis_results['consistency_score']:.1f}%")
            
            # Emit comprehensive results
            self.analysis_results_ready.emit(analysis_results)
            
            logger.info("✅ RealTimeAnalyzerWorker finalizado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro no RealTimeAnalyzerWorker: {e}", exc_info=True)
            self.error.emit(f"Erro durante a análise: {str(e)}")
        finally:
            self._running = False
            self.finished.emit()

    def _analyze_lap(self, lap: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a single lap and returns analysis results."""
        logger.info(f"🔍 Iniciando análise detalhada da volta...")
        
        data_points = lap.get("data_points", [])
        lap_time = lap.get("lap_time", 0)
        
        logger.info(f"   📊 Pontos de dados: {len(data_points)}")
        logger.info(f"   ⏱️ Tempo da volta: {lap_time}")
        
        analysis = {
            "lap_number": lap.get("lap_number", 0),
            "lap_time": lap_time,
            "data_points_count": len(data_points),
            "average_speed": 0.0,
            "max_speed": 0.0,
            "min_speed": 999999.0,  # Valor alto em vez de float('inf')
            "throttle_usage": 0.0,
            "brake_usage": 0.0
        }
        
        if not data_points:
            logger.warning("   ⚠️ Nenhum ponto de dados encontrado!")
            return analysis
        
        logger.info(f"   📈 Analisando {len(data_points)} pontos de dados...")
        
        speeds = []
        throttle_values = []
        brake_values = []
        
        # Log dos primeiros pontos para debug
        for i, point in enumerate(data_points[:5]):  # Primeiros 5 pontos
            logger.info(f"   📊 Ponto {i+1}: {point}")
        
        for i, point in enumerate(data_points):
            # Tenta diferentes nomes de canais para velocidade
            speed = point.get("SPEED", point.get("speed", 0))
            if speed is not None:
                try:
                    speed_float = float(speed)
                    speeds.append(speed_float)
                    analysis["max_speed"] = max(analysis["max_speed"], speed_float)
                    analysis["min_speed"] = min(analysis["min_speed"], speed_float)
                except (ValueError, TypeError) as e:
                    logger.warning(f"   ⚠️ Erro ao converter velocidade: {speed} - {e}")
            
            # Tenta diferentes nomes de canais para acelerador
            throttle = point.get("THROTTLE", point.get("throttle", 0))
            if throttle is not None:
                try:
                    throttle_values.append(float(throttle))
                except (ValueError, TypeError) as e:
                    logger.warning(f"   ⚠️ Erro ao converter throttle: {throttle} - {e}")
            
            # Tenta diferentes nomes de canais para freio
            brake = point.get("BRAKE", point.get("brake", 0))
            if brake is not None:
                try:
                    brake_values.append(float(brake))
                except (ValueError, TypeError) as e:
                    logger.warning(f"   ⚠️ Erro ao converter brake: {brake} - {e}")
        
        logger.info(f"   📊 Valores encontrados:")
        logger.info(f"      Velocidades válidas: {len(speeds)}")
        logger.info(f"      Valores de throttle: {len(throttle_values)}")
        logger.info(f"      Valores de brake: {len(brake_values)}")
        
        if speeds:
            analysis["average_speed"] = sum(speeds) / len(speeds)
            logger.info(f"      Velocidade média: {analysis['average_speed']:.2f}")
            logger.info(f"      Velocidade máxima: {analysis['max_speed']:.2f}")
            logger.info(f"      Velocidade mínima: {analysis['min_speed']:.2f}")
        else:
            logger.warning("   ⚠️ Nenhuma velocidade válida encontrada!")
            
        if throttle_values:
            analysis["throttle_usage"] = sum(throttle_values) / len(throttle_values) * 100
            logger.info(f"      Uso de throttle: {analysis['throttle_usage']:.2f}%")
        else:
            logger.warning("   ⚠️ Nenhum valor de throttle válido encontrado!")
            
        if brake_values:
            analysis["brake_usage"] = sum(brake_values) / len(brake_values) * 100
            logger.info(f"      Uso de brake: {analysis['brake_usage']:.2f}%")
        else:
            logger.warning("   ⚠️ Nenhum valor de brake válido encontrado!")
        
        # Corrige min_speed se não foi encontrado nenhum valor
        if analysis["min_speed"] == 999999.0:
            analysis["min_speed"] = 0.0
            logger.info("   ⚠️ Velocidade mínima corrigida para 0.0")
        
        logger.info(f"   ✅ Análise da volta concluída!")
        return analysis

    def _generate_lap_feedback(self, lap_analysis: Dict[str, Any]) -> str:
        """Generates feedback for a single lap."""
        lap_number = lap_analysis["lap_number"]
        lap_time = lap_analysis["lap_time"]
        avg_speed = lap_analysis["average_speed"]
        
        feedback_parts = []
        
        if lap_time > 0:
            feedback_parts.append(f"Volta {lap_number}: {lap_time:.2f} segundos")
            
            if avg_speed > 150:
                feedback_parts.append("Boa velocidade média")
            elif avg_speed < 100:
                feedback_parts.append("Velocidade média baixa")
        
        return ". ".join(feedback_parts) if feedback_parts else ""

    def _generate_final_feedback(self, analysis_results: Dict[str, Any]) -> str:
        """Generates final feedback after analyzing all laps."""
        total_laps = analysis_results["total_laps"]
        analyzed_laps = analysis_results["laps_analyzed"]
        best_lap = analysis_results["best_lap"]
        worst_lap = analysis_results["worst_lap"]
        consistency = analysis_results["consistency_score"]
        
        feedback_parts = []
        
        feedback_parts.append(f"Análise concluída: {analyzed_laps} voltas analisadas")
        
        if best_lap:
            feedback_parts.append(f"Melhor volta: {best_lap['lap']} em {best_lap['time']:.2f}s")
        
        if consistency > 80:
            feedback_parts.append("Excelente consistência")
        elif consistency > 60:
            feedback_parts.append("Boa consistência")
        else:
            feedback_parts.append("Consistência pode melhorar")
        
        return ". ".join(feedback_parts)

    def stop(self):
        logger.info("Stopping RealTimeAnalyzerWorker...")
        self._running = False
        self._paused = False  # Ensure it's not stuck paused

    def pause(self):
        logger.info("Pausing RealTimeAnalyzerWorker...")
        self._paused = True

    def resume(self):
        logger.info("Resuming RealTimeAnalyzerWorker...")
        self._paused = False

class RealTimeAnalyzer(QObject):
    """Manages the telemetry analysis worker thread."""
    analysis_error = pyqtSignal(str)
    analysis_feedback = pyqtSignal(str)
    analysis_progress = pyqtSignal(int, int)
    analysis_finished = pyqtSignal(dict)  # Agora emite o dicionário de resultados
    analysis_started = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.thread = None
        self._running = False
        self._stop_requested = False

    def start_analysis(self, telemetry_data: Dict[str, Any]):
        """Inicia a análise de telemetria em uma thread separada."""
        logger.info("=== INICIANDO ANÁLISE DE TELEMETRIA ===")
        logger.info(f"Tipo de dados recebidos: {type(telemetry_data)}")
        logger.info(f"Chaves disponíveis: {list(telemetry_data.keys()) if telemetry_data else 'Nenhuma'}")
        
        if not telemetry_data:
            logger.error("❌ Dados de telemetria vazios!")
            self.analysis_error.emit("Dados de telemetria inválidos ou ausentes.")
            return

        # Log detalhado dos dados
        logger.info("=== DETALHES DOS DADOS ===")
        for key, value in telemetry_data.items():
            if isinstance(value, (list, dict)):
                logger.info(f"📊 {key}: {type(value).__name__} com {len(value)} itens")
                if isinstance(value, list) and len(value) > 0:
                    logger.info(f"   Primeiro item: {value[0]}")
                elif isinstance(value, dict) and len(value) > 0:
                    first_key = list(value.keys())[0]
                    logger.info(f"   Primeira chave: {first_key} = {value[first_key]}")
            else:
                logger.info(f"📊 {key}: {value}")

        # Verifica se há laps
        laps = telemetry_data.get("laps", [])
        logger.info(f"🏁 Voltas encontradas: {len(laps)}")
        
        if not laps:
            logger.warning("⚠️ Nenhuma volta encontrada nos dados!")
            logger.info("Tentando encontrar dados alternativos...")
            
            # Tenta encontrar dados em outras estruturas
            if "beacons" in telemetry_data:
                beacons = telemetry_data["beacons"]
                logger.info(f"📡 Beacons encontrados: {len(beacons)}")
                if beacons:
                    logger.info(f"   Primeiro beacon: {beacons[0]}")
                    
            if "data" in telemetry_data:
                data = telemetry_data["data"]
                logger.info(f"📈 Dados encontrados: {type(data)}")
                if hasattr(data, 'shape'):
                    logger.info(f"   Shape: {data.shape}")
                if hasattr(data, 'columns'):
                    logger.info(f"   Colunas: {list(data.columns)}")
                    
            # Cria uma volta artificial se não houver
            logger.info("🔄 Criando volta artificial para análise...")
            artificial_lap = {
                "lap_number": 1,
                "lap_time": 0.0,
                "data_points": []
            }
            
            # Adiciona dados dos beacons se disponível
            if "beacons" in telemetry_data and telemetry_data["beacons"]:
                artificial_lap["data_points"] = telemetry_data["beacons"]
                logger.info(f"   Adicionados {len(telemetry_data['beacons'])} pontos de dados")
                
            # Adiciona dados do DataFrame se disponível
            elif "data" in telemetry_data and hasattr(telemetry_data["data"], 'to_dict'):
                df = telemetry_data["data"]
                records = df.to_dict('records')
                artificial_lap["data_points"] = records
                logger.info(f"   Adicionados {len(records)} pontos de dados do DataFrame")
                
            laps = [artificial_lap]
            telemetry_data["laps"] = laps
            logger.info("✅ Volta artificial criada com sucesso!")

        # Para qualquer análise anterior
        self.stop_analysis()
        
        try:
            # Cria o worker
            self.worker = RealTimeAnalyzerWorker(telemetry_data)
            
            # Cria a thread
            self.thread = QThread()
            self.worker.moveToThread(self.thread)
            
            # Conecta sinais
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            # Conecta sinais de feedback
            self.worker.feedback_detected.connect(self.analysis_feedback)
            self.worker.progress_update.connect(self.analysis_progress)
            self.worker.error.connect(self.analysis_error)
            self.worker.analysis_results_ready.connect(self.analysis_finished)
            
            # Conecta sinal de finalização
            self.thread.finished.connect(self._on_analysis_finished)
            
            # Marca como rodando
            self._running = True
            self._stop_requested = False
            
            # Emite sinal de início
            self.analysis_started.emit()
            
            # Inicia a thread
            self.thread.start()
            
            logger.info("✅ RealTimeAnalyzer thread iniciada com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar análise: {e}", exc_info=True)
            self.analysis_error.emit(f"Erro ao iniciar análise: {str(e)}")
            self._cleanup()

    def _on_analysis_finished(self):
        """Callback quando a análise termina."""
        logger.info("Analysis finished signal received.")
        self._running = False
        self._cleanup()

    def _cleanup(self):
        """Limpa recursos da análise."""
        try:
            if hasattr(self, 'worker') and self.worker:
                self.worker = None
            if hasattr(self, 'thread') and self.thread:
                self.thread = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def stop_analysis(self):
        """Para a análise de telemetria."""
        logger.info("Requesting RealTimeAnalyzer stop...")
        self._running = False
        self._stop_requested = True
        
        try:
            # Para o worker thread
            if hasattr(self, 'worker') and self.worker:
                self.worker.stop()
            
            # Para a thread principal com timeout
            if hasattr(self, 'thread') and self.thread and self.thread.isRunning():
                self.thread.quit()
                if not self.thread.wait(2000):  # Aguarda até 2 segundos
                    logger.warning("RealTimeAnalyzer thread não terminou em tempo hábil")
                    self.thread.terminate()
                    self.thread.wait(1000)  # Aguarda mais um pouco
            
            self._cleanup()
            
        except Exception as e:
            logger.error(f"Error stopping analysis: {e}")
        
        logger.info("RealTimeAnalyzer stopped.")

    def __del__(self):
        """Destrutor para garantir limpeza adequada."""
        try:
            self.stop_analysis()
        except:
            pass  # Ignora erros no destrutor

    def pause_analysis(self):
        """Pausa a análise de telemetria."""
        if hasattr(self, 'worker') and self.worker and self._running:
            self.worker.pause()
            logger.info("Análise pausada")
        else:
            logger.info("Análise não está rodando ou worker não disponível")
              
    def resume_analysis(self):
        """Retoma a análise de telemetria."""
        if hasattr(self, 'worker') and self.worker and self._running:
            self.worker.resume()
            logger.info("Análise retomada")
        else:
            logger.info("Análise não está rodando ou worker não disponível")
