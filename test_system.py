#!/usr/bin/env python3
"""
Teste simples para verificar se o sistema está funcionando.
"""

import sys
import os
import logging

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todos os imports estão funcionando."""
    try:
        logger.info("Testando imports...")
        
        # Testa imports básicos
        from PyQt6.QtWidgets import QApplication
        logger.info("✓ PyQt6 importado com sucesso")
        
        # Testa imports do sistema
        from src.ui.modern_styles import get_modern_stylesheet
        logger.info("✓ Stylesheet importado com sucesso")
        
        from src.parsers.csv_parser import parse_csv_telemetry
        logger.info("✓ CSV parser importado com sucesso")
        
        from src.ui.telemetry_widget import TelemetryWidget
        logger.info("✓ TelemetryWidget importado com sucesso")
        
        # Testa se o stylesheet funciona
        stylesheet = get_modern_stylesheet()
        if stylesheet and len(stylesheet) > 100:
            logger.info("✓ Stylesheet gerado com sucesso")
        else:
            logger.error("✗ Stylesheet vazio ou inválido")
            return False
            
        return True
        
    except ImportError as e:
        logger.error(f"✗ Erro de import: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Erro inesperado: {e}")
        return False

def test_csv_parser():
    """Testa o parser CSV."""
    try:
        logger.info("Testando parser CSV...")
        
        from src.parsers.csv_parser import parse_csv_telemetry
        
        # Testa com um arquivo de exemplo
        csv_file = "exemplos/monza-mclaren_720s_gt3_evo-1-2025.06.01-19.40.55.csv"
        
        if os.path.exists(csv_file):
            data = parse_csv_telemetry(csv_file)
            if data and 'metadata' in data:
                logger.info(f"✓ CSV parseado com sucesso: {data['metadata'].get('filename', 'N/A')}")
                return True
            else:
                logger.error("✗ Dados CSV inválidos")
                return False
        else:
            logger.warning(f"Arquivo de exemplo não encontrado: {csv_file}")
            return True  # Não é um erro crítico
            
    except Exception as e:
        logger.error(f"✗ Erro no parser CSV: {e}")
        return False

def test_ui_creation():
    """Testa a criação da UI."""
    try:
        logger.info("Testando criação da UI...")
        
        from PyQt6.QtWidgets import QApplication
        from src.ui.telemetry_widget import TelemetryWidget
        
        # Cria aplicação
        app = QApplication([])
        
        # Cria widget
        widget = TelemetryWidget()
        widget.show()
        
        logger.info("✓ UI criada com sucesso")
        
        # Fecha após um breve delay
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(1000)  # 1 segundo
        
        app.exec()
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro na criação da UI: {e}")
        return False

def main():
    """Função principal de teste."""
    logger.info("=== TESTE DO SISTEMA RACE TELEMETRY ANALYZER ===")
    
    tests = [
        ("Imports", test_imports),
        ("Parser CSV", test_csv_parser),
        ("UI Creation", test_ui_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testando: {test_name} ---")
        try:
            if test_func():
                logger.info(f"✓ {test_name}: PASSOU")
                passed += 1
            else:
                logger.error(f"✗ {test_name}: FALHOU")
        except Exception as e:
            logger.error(f"✗ {test_name}: ERRO - {e}")
    
    logger.info(f"\n=== RESULTADO: {passed}/{total} testes passaram ===")
    
    if passed == total:
        logger.info("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return 0
    else:
        logger.error("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 