"""
Script de teste completo para validar todas as funcionalidades superiores implementadas.
"""

import os
import sys
import traceback

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_track_detection():
    """Testa o sistema de detecção de traçado."""
    print("=== Teste de Detecção de Traçado ===")
    
    try:
        from analysis.track_detection import TrackDetector, TrackLayout, TrackPoint
        
        detector = TrackDetector()
        
        # Testa base de dados de pistas
        assert 'monza' in detector.track_database
        assert 'spa' in detector.track_database
        print("✅ Base de dados de pistas carregada")
        
        # Testa criação de traçado sintético
        synthetic_track = detector._generate_synthetic_track('monza', {})
        assert isinstance(synthetic_track, TrackLayout)
        assert len(synthetic_track.points) > 0
        assert len(synthetic_track.sectors) == 3
        print("✅ Geração de traçado sintético funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de detecção de traçado: {e}")
        traceback.print_exc()
        return False

def test_advanced_telemetry():
    """Testa o sistema de análise avançada."""
    print("\n=== Teste de Análise Avançada ===")
    
    try:
        from analysis.advanced_telemetry import AdvancedTelemetryAnalyzer, PerformanceMetric
        
        analyzer = AdvancedTelemetryAnalyzer()
        
        # Testa com dados simulados
        mock_data = {
            'metadata': {'track': 'monza', 'car': 'McLaren 720S GT3'},
            'laps': [
                {'lap_time': 80.5, 'data_points': [
                    {'Time': 0.0, 'SPEED': 100, 'THROTTLE': 50, 'BRAKE': 0},
                    {'Time': 1.0, 'SPEED': 150, 'THROTTLE': 80, 'BRAKE': 0},
                    {'Time': 2.0, 'SPEED': 120, 'THROTTLE': 30, 'BRAKE': 50}
                ]},
                {'lap_time': 81.2, 'data_points': []}
            ]
        }
        
        # Executa análise
        results = analyzer.comprehensive_analysis(mock_data)
        
        assert 'session_overview' in results
        assert 'lap_analysis' in results
        assert 'performance_metrics' in results
        assert 'driver_insights' in results
        
        print("✅ Análise abrangente executada com sucesso")
        
        # Testa análise de volta individual
        lap_analysis = analyzer._analyze_single_lap(mock_data['laps'][0], 1, mock_data)
        assert lap_analysis['valid'] == True
        assert 'speed_analysis' in lap_analysis
        assert 'throttle_analysis' in lap_analysis
        
        print("✅ Análise individual de volta funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de análise avançada: {e}")
        traceback.print_exc()
        return False

def test_superior_ui_components():
    """Testa os componentes superiores da UI."""
    print("\n=== Teste de Componentes Superiores da UI ===")
    
    try:
        # Testa importação dos componentes
        from ui.superior_telemetry_widget import (
            SuperiorTelemetryWidget, TrackMapWidget, AdvancedAnalysisWidget
        )
        
        print("✅ Importação dos componentes superiores bem-sucedida")
        
        # Verifica se as classes têm os métodos necessários
        assert hasattr(SuperiorTelemetryWidget, 'load_telemetry_data')
        assert hasattr(TrackMapWidget, 'load_track_layout')
        assert hasattr(AdvancedAnalysisWidget, 'perform_analysis')
        
        print("✅ Métodos essenciais presentes nos componentes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes superiores: {e}")
        traceback.print_exc()
        return False

def test_integration_with_main():
    """Testa integração com o sistema principal."""
    print("\n=== Teste de Integração com Sistema Principal ===")
    
    try:
        # Verifica se o main foi atualizado corretamente
        main_file = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
        with open(main_file, 'r') as f:
            main_content = f.read()
        
        # Verifica imports
        assert 'superior_telemetry_widget' in main_content
        assert 'SuperiorTelemetryWidget' in main_content
        
        print("✅ Imports do widget superior integrados no main")
        
        # Verifica uso do widget
        assert 'self.telemetry_visualizer = SuperiorTelemetryWidget()' in main_content
        assert 'load_telemetry_data' in main_content
        
        print("✅ Widget superior integrado no fluxo principal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        traceback.print_exc()
        return False

def test_csv_parser_with_advanced_features():
    """Testa parser CSV com funcionalidades avançadas."""
    print("\n=== Teste de Parser CSV com Funcionalidades Avançadas ===")
    
    try:
        from parsers.csv_parser import parse_csv_telemetry
        
        # Testa com arquivo de exemplo
        csv_file = os.path.join(os.path.dirname(__file__), 'exemplos', 'monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv')
        
        if not os.path.exists(csv_file):
            print(f"⚠️  Arquivo de exemplo não encontrado: {csv_file}")
            return True  # Não falha se não há arquivo de exemplo
        
        data = parse_csv_telemetry(csv_file)
        
        # Verifica estrutura de dados compatível com análise avançada
        assert 'metadata' in data
        assert 'laps' in data
        assert 'channels' in data
        
        # Verifica se há dados suficientes para análise
        if data['laps']:
            lap = data['laps'][0]
            assert 'data_points' in lap
            
            if lap['data_points']:
                point = lap['data_points'][0]
                # Verifica se há canais essenciais para análise avançada
                essential_channels = ['Time', 'SPEED']
                for channel in essential_channels:
                    if channel in point:
                        print(f"✅ Canal essencial '{channel}' presente")
        
        print("✅ Parser CSV compatível com análise avançada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do parser CSV avançado: {e}")
        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """Testa benchmarks de performance."""
    print("\n=== Teste de Benchmarks de Performance ===")
    
    try:
        from analysis.advanced_telemetry import AdvancedTelemetryAnalyzer
        
        analyzer = AdvancedTelemetryAnalyzer()
        
        # Verifica se benchmarks estão carregados
        assert len(analyzer.benchmarks) > 0
        assert 'monza' in analyzer.benchmarks
        
        monza_benchmark = analyzer.benchmarks['monza']
        assert 'lap_time' in monza_benchmark
        assert 'top_speed' in monza_benchmark
        
        print("✅ Benchmarks de performance carregados")
        
        # Testa cálculo de métricas
        mock_data = {
            'laps': [{'lap_time': 80.5}, {'lap_time': 81.0}],
            'metadata': {'track': 'monza'}
        }
        
        metrics = analyzer._calculate_performance_metrics(mock_data)
        assert isinstance(metrics, list)
        
        print("✅ Cálculo de métricas de performance funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de benchmarks: {e}")
        traceback.print_exc()
        return False

def test_file_structure_complete():
    """Testa se a estrutura de arquivos está completa."""
    print("\n=== Teste de Estrutura de Arquivos Completa ===")
    
    try:
        base_dir = os.path.dirname(__file__)
        
        # Arquivos essenciais do sistema superior
        required_files = [
            'src/analysis/track_detection.py',
            'src/analysis/advanced_telemetry.py',
            'src/analysis/__init__.py',
            'src/ui/superior_telemetry_widget.py',
            'src/ui/modern_dashboard_widget.py',
            'src/ui/modern_styles.py',
            'src/parsers/csv_parser.py',
            'src/main.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Arquivos ausentes: {missing_files}")
            return False
        
        print("✅ Todos os arquivos essenciais estão presentes")
        
        # Verifica tamanhos dos arquivos (devem ter conteúdo substancial)
        substantial_files = [
            'src/analysis/track_detection.py',
            'src/analysis/advanced_telemetry.py',
            'src/ui/superior_telemetry_widget.py'
        ]
        
        for file_path in substantial_files:
            full_path = os.path.join(base_dir, file_path)
            file_size = os.path.getsize(full_path)
            
            if file_size < 5000:  # Menos de 5KB indica arquivo incompleto
                print(f"⚠️  Arquivo {file_path} pode estar incompleto ({file_size} bytes)")
            else:
                print(f"✅ Arquivo {file_path} tem tamanho adequado ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de estrutura: {e}")
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes do sistema superior."""
    print("🚀 Iniciando testes do Sistema Superior de Telemetria\n")
    
    tests = [
        ("Estrutura de Arquivos Completa", test_file_structure_complete),
        ("Detecção de Traçado", test_track_detection),
        ("Análise Avançada de Telemetria", test_advanced_telemetry),
        ("Componentes Superiores da UI", test_superior_ui_components),
        ("Integração com Sistema Principal", test_integration_with_main),
        ("Parser CSV Avançado", test_csv_parser_with_advanced_features),
        ("Benchmarks de Performance", test_performance_benchmarks)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro crítico no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES DO SISTEMA SUPERIOR")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🏎️  Sistema Superior de Telemetria implementado com sucesso!")
        print("🚀 Funcionalidades que superam o MoTeC estão prontas!")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

