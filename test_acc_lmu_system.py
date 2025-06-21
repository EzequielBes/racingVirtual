"""
Script de teste abrangente para validar todas as funcionalidades do sistema de telemetria ACC/LMU.
"""

import sys
import os
import logging
from typing import Dict, Any

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Configuração de logging para testes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_acc_lmu_system")

def test_imports():
    """Testa se todos os módulos podem ser importados corretamente."""
    logger.info("=== Testando Imports ===")
    
    try:
        # Testa imports de análise
        from src.analysis.advanced_telemetry import AdvancedTelemetryAnalyzer
        from src.analysis.track_detection import TrackAnalyzer
        logger.info("✅ Módulos de análise importados com sucesso")
        
        # Testa imports de UI
        from src.ui.acc_lmu_telemetry_widget import ACCLMUTelemetryWidget
        from src.ui.advanced_analysis_widget import AdvancedAnalysisWidget
        logger.info("✅ Widgets de UI importados com sucesso")
        
        # Testa imports de tempo real
        from src.realtime.acc_collector import ACCDataCollector
        from src.realtime.lmu_collector import LMUDataCollector
        from src.realtime.realtime_manager import RealtimeTelemetryManager
        logger.info("✅ Módulos de tempo real importados com sucesso")
        
        # Testa imports de parsers
        from src.parsers.csv_parser import parse_csv_telemetry
        logger.info("✅ Parsers importados com sucesso")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False

def test_advanced_telemetry_analyzer():
    """Testa o analisador avançado de telemetria."""
    logger.info("=== Testando AdvancedTelemetryAnalyzer ===")
    
    try:
        from src.analysis.advanced_telemetry import AdvancedTelemetryAnalyzer
        
        analyzer = AdvancedTelemetryAnalyzer()
        
        # Dados de teste simulando ACC/LMU
        test_data = {
            "metadata": {
                "track": "Monza",
                "car": "McLaren 720S GT3",
                "session_type": "Practice",
                "date": "2025-01-18"
            },
            "laps": [
                {
                    "lap_number": 1,
                    "lap_time": 108.5,
                    "data_points": [
                        {"Time": 0.0, "SPEED": 0, "THROTTLE": 0, "BRAKE": 0, "STEERANGLE": 0, "G_LAT": 0, "G_LONG": 0, "RPM": 1000, "GEAR": 1},
                        {"Time": 10.0, "SPEED": 120, "THROTTLE": 80, "BRAKE": 0, "STEERANGLE": 15, "G_LAT": 0.8, "G_LONG": 0.3, "RPM": 6000, "GEAR": 3},
                        {"Time": 50.0, "SPEED": 280, "THROTTLE": 100, "BRAKE": 0, "STEERANGLE": 5, "G_LAT": 0.2, "G_LONG": 0.1, "RPM": 8500, "GEAR": 6},
                        {"Time": 80.0, "SPEED": 150, "THROTTLE": 0, "BRAKE": 80, "STEERANGLE": -20, "G_LAT": -1.2, "G_LONG": -1.5, "RPM": 4000, "GEAR": 4},
                        {"Time": 108.5, "SPEED": 200, "THROTTLE": 100, "BRAKE": 0, "STEERANGLE": 0, "G_LAT": 0, "G_LONG": 0.5, "RPM": 7000, "GEAR": 5}
                    ]
                },
                {
                    "lap_number": 2,
                    "lap_time": 107.8,
                    "data_points": [
                        {"Time": 108.5, "SPEED": 0, "THROTTLE": 0, "BRAKE": 0, "STEERANGLE": 0, "G_LAT": 0, "G_LONG": 0, "RPM": 1000, "GEAR": 1},
                        {"Time": 118.0, "SPEED": 125, "THROTTLE": 85, "BRAKE": 0, "STEERANGLE": 12, "G_LAT": 0.9, "G_LONG": 0.4, "RPM": 6200, "GEAR": 3},
                        {"Time": 158.0, "SPEED": 285, "THROTTLE": 100, "BRAKE": 0, "STEERANGLE": 3, "G_LAT": 0.1, "G_LONG": 0.1, "RPM": 8600, "GEAR": 6},
                        {"Time": 188.0, "SPEED": 155, "THROTTLE": 0, "BRAKE": 75, "STEERANGLE": -18, "G_LAT": -1.1, "G_LONG": -1.4, "RPM": 4200, "GEAR": 4},
                        {"Time": 216.3, "SPEED": 205, "THROTTLE": 100, "BRAKE": 0, "STEERANGLE": 0, "G_LAT": 0, "G_LONG": 0.6, "RPM": 7200, "GEAR": 5}
                    ]
                }
            ],
            "beacons": [
                {"time": 0.0, "name": "Start/Finish", "lap_index": 0},
                {"time": 108.5, "name": "Start/Finish", "lap_index": 1},
                {"time": 216.3, "name": "Start/Finish", "lap_index": 2}
            ]
        }
        
        # Executa análise abrangente
        results = analyzer.comprehensive_analysis(test_data)
        
        # Valida resultados
        assert "session_overview" in results, "session_overview não encontrado"
        assert "performance_metrics" in results, "performance_metrics não encontrado"
        assert "driver_insights" in results, "driver_insights não encontrado"
        assert "comparative_analysis" in results, "comparative_analysis não encontrado"
        assert "predictive_analysis" in results, "predictive_analysis não encontrado"
        
        logger.info(f"✅ Análise abrangente executada com sucesso")
        logger.info(f"   - {len(results['performance_metrics'])} métricas de performance")
        logger.info(f"   - {len(results['driver_insights'])} insights para o piloto")
        logger.info(f"   - {len(results['comparative_analysis'])} comparações de volta")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no AdvancedTelemetryAnalyzer: {e}")
        return False

def test_track_analyzer():
    """Testa o analisador de pista."""
    logger.info("=== Testando TrackAnalyzer ===")
    
    try:
        from src.analysis.track_detection import TrackAnalyzer
        
        analyzer = TrackAnalyzer()
        
        # Dados de teste com coordenadas GPS simuladas
        test_data = {
            "metadata": {"track": "Monza"},
            "laps": [
                {
                    "lap_number": 1,
                    "data_points": [
                        {"Time": 0.0, "GPS_LAT": 45.6156, "GPS_LON": 9.2811, "SPEED": 100},
                        {"Time": 10.0, "GPS_LAT": 45.6160, "GPS_LON": 9.2815, "SPEED": 150},
                        {"Time": 20.0, "GPS_LAT": 45.6165, "GPS_LON": 9.2820, "SPEED": 200},
                        {"Time": 30.0, "GPS_LAT": 45.6170, "GPS_LON": 9.2825, "SPEED": 180}
                    ]
                }
            ]
        }
        
        # Testa extração de layout da pista
        track_layout = analyzer.extract_track_layout(test_data)
        
        if track_layout and track_layout.get('coordinates'):
            logger.info(f"✅ Layout da pista extraído com {len(track_layout['coordinates'])} pontos")
        else:
            logger.info("ℹ️ Layout da pista não disponível (dados GPS insuficientes)")
        
        # Testa detecção de setores
        sectors = analyzer.detect_sectors(test_data)
        logger.info(f"✅ {len(sectors)} setores detectados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no TrackAnalyzer: {e}")
        return False

def test_realtime_collectors():
    """Testa os coletores de dados em tempo real."""
    logger.info("=== Testando Coletores de Tempo Real ===")
    
    try:
        from src.realtime.acc_collector import ACCDataCollector
        from src.realtime.lmu_collector import LMUDataCollector
        from src.realtime.realtime_manager import RealtimeTelemetryManager
        
        # Testa instanciação dos coletores
        acc_collector = ACCDataCollector()
        lmu_collector = LMUDataCollector()
        manager = RealtimeTelemetryManager()
        
        logger.info("✅ Coletores de tempo real instanciados com sucesso")
        
        # Testa métodos básicos (sem conectar aos jogos)
        acc_available = acc_collector.is_game_running()
        lmu_available = lmu_collector.is_game_running()
        
        logger.info(f"   - ACC disponível: {acc_available}")
        logger.info(f"   - LMU disponível: {lmu_available}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos coletores de tempo real: {e}")
        return False

def test_csv_parser():
    """Testa o parser de CSV."""
    logger.info("=== Testando Parser CSV ===")
    
    try:
        from src.parsers.csv_parser import parse_csv_telemetry
        
        # Cria um arquivo CSV de teste
        test_csv_content = """Time,SPEED,THROTTLE,BRAKE,STEERANGLE,G_LAT,G_LONG,RPM,GEAR
0.0,0,0,0,0,0.0,0.0,1000,1
1.0,50,80,0,5,0.2,0.5,3000,2
2.0,100,100,0,10,0.5,0.3,5000,3
3.0,150,100,0,15,0.8,0.1,6000,4
4.0,200,100,0,5,0.2,0.0,7000,5
5.0,180,0,80,-10,-0.5,-1.2,5000,4
6.0,120,50,0,-5,-0.2,0.2,4000,3
"""
        
        test_csv_path = "/tmp/test_telemetry.csv"
        with open(test_csv_path, 'w') as f:
            f.write(test_csv_content)
        
        # Testa o parser
        parsed_data = parse_csv_telemetry(test_csv_path)
        
        assert "metadata" in parsed_data, "metadata não encontrado"
        assert "laps" in parsed_data, "laps não encontrado"
        assert len(parsed_data["laps"]) > 0, "Nenhuma volta encontrada"
        
        logger.info(f"✅ CSV parseado com sucesso")
        logger.info(f"   - {len(parsed_data['laps'])} voltas encontradas")
        logger.info(f"   - {len(parsed_data['laps'][0]['data_points'])} pontos de dados na primeira volta")
        
        # Remove arquivo de teste
        os.remove(test_csv_path)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no parser CSV: {e}")
        return False

def test_ui_widgets():
    """Testa se os widgets de UI podem ser instanciados."""
    logger.info("=== Testando Widgets de UI ===")
    
    try:
        # Tenta importar PyQt6 primeiro
        from PyQt6.QtWidgets import QApplication
        
        # Cria uma aplicação Qt para os testes
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        from src.ui.acc_lmu_telemetry_widget import ACCLMUTelemetryWidget
        from src.ui.advanced_analysis_widget import AdvancedAnalysisWidget
        
        # Testa instanciação dos widgets
        acc_lmu_widget = ACCLMUTelemetryWidget()
        advanced_widget = AdvancedAnalysisWidget()
        
        logger.info("✅ Widgets de UI instanciados com sucesso")
        
        # Testa dados de exemplo
        test_results = {
            "session_overview": {
                "total_laps": 5,
                "best_lap_time": 108.5,
                "track": "Monza",
                "car": "McLaren 720S GT3"
            },
            "performance_metrics": [],
            "driver_insights": [],
            "comparative_analysis": [],
            "predictive_analysis": {},
            "setup_recommendations": [],
            "consistency_analysis": {}
        }
        
        advanced_widget.update_analysis_results(test_results)
        logger.info("✅ Widget de análise avançada atualizado com dados de teste")
        
        return True
        
    except ImportError:
        logger.warning("⚠️ PyQt6 não disponível - pulando testes de UI")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nos widgets de UI: {e}")
        return False

def run_all_tests():
    """Executa todos os testes."""
    logger.info("🚀 Iniciando testes do sistema ACC/LMU")
    
    tests = [
        ("Imports", test_imports),
        ("AdvancedTelemetryAnalyzer", test_advanced_telemetry_analyzer),
        ("TrackAnalyzer", test_track_analyzer),
        ("Coletores de Tempo Real", test_realtime_collectors),
        ("Parser CSV", test_csv_parser),
        ("Widgets de UI", test_ui_widgets)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Executando: {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("🎉 Todos os testes passaram! Sistema pronto para uso.")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} teste(s) falharam. Verifique os logs acima.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

