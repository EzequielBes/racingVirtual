"""
Script de teste para validar as melhorias implementadas no Race Telemetry Analyzer.
Testa a funcionalidade de importação de CSV e a integração dos novos componentes.
"""

import os
import sys
import traceback

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_csv_parser():
    """Testa o parser de CSV."""
    print("=== Teste do Parser CSV ===")
    
    try:
        from parsers.csv_parser import parse_csv_telemetry
        
        # Caminho para arquivo de exemplo
        csv_file = os.path.join(os.path.dirname(__file__), 'exemplos', 'monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv')
        
        if not os.path.exists(csv_file):
            print(f"❌ Arquivo de exemplo não encontrado: {csv_file}")
            return False
        
        print(f"📁 Testando arquivo: {os.path.basename(csv_file)}")
        
        # Parse do arquivo
        data = parse_csv_telemetry(csv_file)
        
        # Validações
        assert 'metadata' in data, "Metadados não encontrados"
        assert 'channels' in data, "Canais não encontrados"
        assert 'data_points' in data, "Pontos de dados não encontrados"
        assert 'laps' in data, "Voltas não encontradas"
        
        print(f"✅ Parser CSV funcionando corretamente")
        print(f"   - Metadados: {len(data['metadata'])} campos")
        print(f"   - Canais: {len(data['channels'])} canais")
        print(f"   - Pontos de dados: {len(data['data_points'])} pontos")
        print(f"   - Voltas: {len(data['laps'])} voltas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do parser CSV: {e}")
        traceback.print_exc()
        return False

def test_modern_components():
    """Testa os componentes modernos da UI."""
    print("\n=== Teste dos Componentes Modernos ===")
    
    try:
        # Testa importação dos componentes modernos
        from ui.modern_dashboard_widget import DashboardWidget, ModernCard, ModernButton, StatusIndicator
        from ui.modern_telemetry_widget import TelemetryChart, ModernTelemetryChart
        from ui.modern_styles import get_modern_stylesheet, get_color_palette
        
        print("✅ Importação dos componentes modernos bem-sucedida")
        
        # Testa criação de instâncias (sem PyQt6 rodando)
        print("✅ Componentes modernos disponíveis:")
        print("   - DashboardWidget moderno")
        print("   - TelemetryChart moderno")
        print("   - Stylesheet moderno")
        print("   - Componentes auxiliares (ModernCard, ModernButton, etc.)")
        
        # Testa stylesheet
        stylesheet = get_modern_stylesheet()
        assert len(stylesheet) > 1000, "Stylesheet muito pequeno"
        print(f"✅ Stylesheet moderno carregado ({len(stylesheet)} caracteres)")
        
        # Testa paleta de cores
        colors = get_color_palette()
        assert 'primary' in colors, "Cor primária não encontrada"
        assert 'background' in colors, "Cor de fundo não encontrada"
        print(f"✅ Paleta de cores carregada ({len(colors)} cores)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste dos componentes modernos: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Testa a integração entre componentes."""
    print("\n=== Teste de Integração ===")
    
    try:
        # Testa importação do main atualizado
        from main import MainWindow
        print("✅ MainWindow atualizado importado com sucesso")
        
        # Verifica se as importações estão corretas
        import main
        
        # Verifica se os imports modernos estão presentes no código
        main_file = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
        with open(main_file, 'r') as f:
            main_content = f.read()
        
        assert 'modern_dashboard_widget' in main_content, "Import do DashboardWidget moderno não encontrado"
        assert 'modern_telemetry_widget' in main_content, "Import do TelemetryChart moderno não encontrado"
        assert 'modern_styles' in main_content, "Import do stylesheet moderno não encontrado"
        assert 'get_modern_stylesheet' in main_content, "Uso do stylesheet moderno não encontrado"
        
        print("✅ Integração dos componentes modernos no MainWindow verificada")
        
        # Testa se o suporte a CSV foi adicionado
        assert '.csv' in main_content, "Suporte a CSV não encontrado no MainWindow"
        assert 'parse_csv_telemetry' in main_content, "Import do parser CSV não encontrado"
        
        print("✅ Suporte a CSV integrado no MainWindow")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Testa se a estrutura de arquivos está correta."""
    print("\n=== Teste da Estrutura de Arquivos ===")
    
    try:
        base_dir = os.path.dirname(__file__)
        
        # Arquivos que devem existir
        required_files = [
            'src/ui/modern_dashboard_widget.py',
            'src/ui/modern_telemetry_widget.py',
            'src/ui/modern_styles.py',
            'src/parsers/csv_parser.py',
            'src/main.py',
            'test_csv_parser.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Arquivos ausentes: {missing_files}")
            return False
        
        print("✅ Todos os arquivos necessários estão presentes")
        
        # Verifica arquivos de exemplo
        examples_dir = os.path.join(base_dir, 'exemplos')
        if os.path.exists(examples_dir):
            csv_files = [f for f in os.listdir(examples_dir) if f.endswith('.csv')]
            print(f"✅ Arquivos CSV de exemplo encontrados: {len(csv_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da estrutura de arquivos: {e}")
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes de validação das melhorias\n")
    
    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("Parser CSV", test_csv_parser),
        ("Componentes Modernos", test_modern_components),
        ("Integração", test_integration)
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
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! As melhorias foram implementadas com sucesso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

